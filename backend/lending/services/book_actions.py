from datetime import timedelta
from uuid import UUID

from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.utils import timezone

from accounts.models import AppUser
from books.models import Book, BookCopy
from lending.models import MAX_EXTENSION_COUNT, Lending, Reservation

DEFAULT_LENDING_DAYS = 30
DEFAULT_EXTENSION_DAYS = 10


class ActionConflictError(Exception):
    """業務状態により lending action を実行できない場合の例外。"""


class BookNotFoundError(Exception):
    """指定された書籍が見つからない場合の例外。"""


class LendingNotFoundError(Exception):
    """指定された貸出が見つからない場合の例外。"""


def borrow_book(user: AppUser, book_id: UUID) -> Lending:
    with transaction.atomic():
        if not Book.objects.filter(pk=book_id).exists():
            raise BookNotFoundError("書籍が見つかりません")

        if (
            Lending.objects.select_for_update()
            .filter(
                user=user,
                book_copy__book_id=book_id,
                returned_date__isnull=True,
            )
            .exists()
        ):
            raise ActionConflictError("すでにこの本を利用中です")

        if (
            Reservation.objects.select_for_update()
            .filter(
                user=user,
                book_copy__book_id=book_id,
            )
            .exists()
        ):
            raise ActionConflictError("すでにこの本を予約中です")

        book_copy = (
            BookCopy.objects.select_for_update()
            .filter(book_id=book_id, status=BookCopy.Status.AVAILABLE)
            .order_by("id")
            .first()
        )
        if book_copy is None:
            raise ActionConflictError("貸出可能な蔵書がありません")

        borrowed_date = timezone.localdate()
        lending = Lending.objects.create(
            book_copy=book_copy,
            user=user,
            borrowed_date=borrowed_date,
            due_date=borrowed_date + timedelta(days=DEFAULT_LENDING_DAYS - 1), # 当日も含めた30日にするための-1
        )
        book_copy.status = BookCopy.Status.ON_LOAN
        book_copy.save(update_fields=["status", "updated_at"])

    return lending


def list_current_lendings(user: AppUser):
    return (
        Lending.objects.select_related("book_copy", "book_copy__book")
        .filter(
            user=user,
            returned_date__isnull=True,
        )
        .order_by("due_date", "created_at")
    )


def list_lending_history(user: AppUser):
    return (
        Lending.objects.select_related("book_copy", "book_copy__book")
        .filter(
            user=user,
            returned_date__isnull=False,
        )
        .order_by("-returned_date", "-created_at")
    )


def return_lending(user: AppUser, lending_id: UUID) -> Lending:
    with transaction.atomic():
        lending = _get_locked_lending(lending_id)
        _ensure_lending_owner(lending, user)
        _ensure_active_lending(lending)

        book_copy = BookCopy.objects.select_for_update().get(pk=lending.book_copy_id)
        _ensure_book_copy_on_loan(book_copy)

        lending.returned_date = timezone.localdate()
        lending.save(update_fields=["returned_date", "updated_at"])

        book_copy.status = BookCopy.Status.AVAILABLE
        book_copy.save(update_fields=["status", "updated_at"])

    return lending


def extend_lending(user: AppUser, lending_id: UUID) -> Lending:
    with transaction.atomic():
        lending = _get_locked_lending(lending_id)
        _ensure_lending_owner(lending, user)
        _ensure_active_lending(lending)

        book_copy = BookCopy.objects.select_for_update().get(pk=lending.book_copy_id)
        _ensure_book_copy_on_loan(book_copy)

        if lending.extension_count >= MAX_EXTENSION_COUNT:
            raise ActionConflictError("延長回数の上限に達しています")

        lending.due_date += timedelta(days=DEFAULT_EXTENSION_DAYS)
        lending.extension_count += 1
        lending.save(update_fields=["due_date", "extension_count", "updated_at"])

    return lending


def _get_locked_lending(lending_id: UUID) -> Lending:
    try:
        return Lending.objects.select_for_update().get(pk=lending_id)
    except Lending.DoesNotExist as error:
        raise LendingNotFoundError("貸出が見つかりません") from error


def _ensure_lending_owner(lending: Lending, user: AppUser) -> None:
    if lending.user_id != user.id:
        raise PermissionDenied("この貸出を操作する権限がありません")


def _ensure_active_lending(lending: Lending) -> None:
    if lending.returned_date is not None:
        raise ActionConflictError("返却済みの貸出です")


def _ensure_book_copy_on_loan(book_copy: BookCopy) -> None:
    if book_copy.status != BookCopy.Status.ON_LOAN:
        raise ActionConflictError("貸出中の蔵書ではありません")
