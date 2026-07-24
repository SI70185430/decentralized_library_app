from datetime import timedelta
from uuid import UUID

from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.utils import timezone

from accounts.models import AppUser
from books.models import Book, BookCopy
from config.api_errors import ApiErrorCode, DomainError
from lending.models import MAX_EXTENSION_COUNT, Lending, Reservation
from lending.services.borrowing_limits import (
    MAX_CONCURRENT_LENDING_AND_RESERVATION_COUNT,
    lock_user_and_get_current_usage,
)

DEFAULT_LENDING_DAYS = 30
DEFAULT_EXTENSION_DAYS = 10


class ActionConflictError(DomainError):
    """業務状態により lending action を実行できない場合の例外。"""


class BookNotFoundError(DomainError):
    """指定された書籍が見つからない場合の例外。"""

    def __init__(self):
        super().__init__(ApiErrorCode.BOOK_NOT_FOUND)


class LendingNotFoundError(DomainError):
    """指定された貸出が見つからない場合の例外。"""

    def __init__(self):
        super().__init__(ApiErrorCode.LENDING_NOT_FOUND)


def borrow_book(user: AppUser, book_id: UUID) -> Lending:
    with transaction.atomic():
        if not Book.objects.filter(pk=book_id).exists():
            raise BookNotFoundError()

        current_usage = lock_user_and_get_current_usage(user)
        if current_usage >= MAX_CONCURRENT_LENDING_AND_RESERVATION_COUNT:
            raise ActionConflictError(ApiErrorCode.BORROWING_LIMIT_REACHED)

        if (
            Lending.objects.select_for_update()
            .filter(
                user=user,
                book_copy__book_id=book_id,
                returned_date__isnull=True,
            )
            .exists()
        ):
            raise ActionConflictError(ApiErrorCode.ALREADY_BORROWING_BOOK)

        if (
            Reservation.objects.select_for_update()
            .filter(
                user=user,
                book_copy__book_id=book_id,
            )
            .exists()
        ):
            raise ActionConflictError(ApiErrorCode.ALREADY_RESERVING_BOOK)

        book_copy = (
            BookCopy.objects.select_for_update()
            .filter(book_id=book_id, status=BookCopy.Status.AVAILABLE)
            .order_by("id")
            .first()
        )
        if book_copy is None:
            raise ActionConflictError(ApiErrorCode.NO_AVAILABLE_BOOK_COPY)

        borrowed_date = timezone.localdate()
        lending = Lending.objects.create(
            book_copy=book_copy,
            user=user,
            borrowed_date=borrowed_date,
            due_date=borrowed_date
            + timedelta(days=DEFAULT_LENDING_DAYS - 1),  # 当日も含めた30日にするための-1
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
        .order_by("-returned_date", "-created_at")[:10]
    )


def get_lending_detail(user: AppUser, lending_id: UUID) -> Lending:
    try:
        return Lending.objects.select_related("book_copy", "book_copy__book").get(
            pk=lending_id,
            user=user,
        )
    except Lending.DoesNotExist as error:
        raise LendingNotFoundError() from error


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
            raise ActionConflictError(ApiErrorCode.LENDING_EXTENSION_LIMIT_REACHED)

        lending.due_date += timedelta(days=DEFAULT_EXTENSION_DAYS)
        lending.extension_count += 1
        lending.save(update_fields=["due_date", "extension_count", "updated_at"])

    return lending


def _get_locked_lending(lending_id: UUID) -> Lending:
    try:
        return Lending.objects.select_for_update().get(pk=lending_id)
    except Lending.DoesNotExist as error:
        raise LendingNotFoundError() from error


def _ensure_lending_owner(lending: Lending, user: AppUser) -> None:
    if lending.user_id != user.id:
        raise PermissionDenied()


def _ensure_active_lending(lending: Lending) -> None:
    if lending.returned_date is not None:
        raise ActionConflictError(ApiErrorCode.LENDING_ALREADY_RETURNED)


def _ensure_book_copy_on_loan(book_copy: BookCopy) -> None:
    if book_copy.status != BookCopy.Status.ON_LOAN:
        raise ActionConflictError(ApiErrorCode.BOOK_COPY_NOT_ON_LOAN)
