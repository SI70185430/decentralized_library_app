from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING
from uuid import UUID

from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.http import Http404
from django.utils import timezone

from books.models import Book, BookCopy
from lending.models import Lending

if TYPE_CHECKING:
    from accounts.models import AppUser

DEFAULT_LENDING_DAYS = 30
DEFAULT_EXTENSION_DAYS = 10
MAX_EXTENSION_COUNT = 3


class ActionConflictError(Exception):
    """業務状態により lending action を実行できない場合の例外。"""


def borrow_book(*, user: AppUser, book_id: UUID) -> Lending:
    with transaction.atomic():
        try:
            Book.objects.select_for_update().get(pk=book_id)
        except Book.DoesNotExist as error:
            raise Http404("書籍が見つかりません") from error

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
            due_date=borrowed_date + timedelta(days=DEFAULT_LENDING_DAYS),
        )
        book_copy.status = BookCopy.Status.ON_LOAN
        book_copy.save(update_fields=["status", "updated_at"])

    return lending


def return_lending(*, user: AppUser, lending_id: UUID) -> Lending:
    with transaction.atomic():
        lending = _get_locked_lending(lending_id)
        _ensure_lending_owner(lending, user)
        _ensure_active_lending(lending)

        book_copy = BookCopy.objects.select_for_update().get(pk=lending.book_copy_id)
        lending.returned_date = timezone.localdate()
        lending.save(update_fields=["returned_date", "updated_at"])

        book_copy.status = BookCopy.Status.AVAILABLE
        book_copy.save(update_fields=["status", "updated_at"])

    return lending


def extend_lending(*, user: AppUser, lending_id: UUID) -> Lending:
    with transaction.atomic():
        lending = _get_locked_lending(lending_id)
        _ensure_lending_owner(lending, user)
        _ensure_active_lending(lending)

        if lending.extension_count >= MAX_EXTENSION_COUNT:
            raise ActionConflictError("延長回数の上限に達しています")

        lending.due_date += timedelta(days=DEFAULT_EXTENSION_DAYS)
        lending.extension_count += 1
        lending.save(update_fields=["due_date", "extension_count", "updated_at"])

    return lending


def _get_locked_lending(lending_id: UUID) -> Lending:
    try:
        return Lending.objects.select_for_update().select_related("book_copy").get(pk=lending_id)
    except Lending.DoesNotExist as error:
        raise Http404("貸出が見つかりません") from error


def _ensure_lending_owner(lending: Lending, user: AppUser) -> None:
    if lending.user_id != user.id:
        raise PermissionDenied("この貸出を操作する権限がありません")


def _ensure_active_lending(lending: Lending) -> None:
    if lending.returned_date is not None:
        raise ActionConflictError("返却済みの貸出です")
