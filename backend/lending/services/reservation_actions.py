from datetime import timedelta
from uuid import UUID

from django.core.exceptions import PermissionDenied
from django.db import IntegrityError, transaction
from django.utils import timezone

from accounts.models import AppUser
from books.models import Book, BookCopy
from lending.models import Lending, Reservation
from lending.services.book_actions import (
    DEFAULT_LENDING_DAYS,
    ActionConflictError,
    BookNotFoundError,
)

DEFAULT_RESERVATION_HOLD_DAYS = 10


class ReservationNotFoundError(Exception):
    """指定された予約が見つからない場合の例外。"""


# 「基準日」を外から渡せる余地があると保守性・確認容易性が向上するため、引数として渡せるように記述
def release_expired_reservations(reference_date=None) -> int:
    """基準日より前に期限切れとなった予約を削除し、予約中の蔵書を利用可能に戻す。"""
    if reference_date is None:
        reference_date = timezone.localdate()

    released_count = 0
    with transaction.atomic():
        reservations = Reservation.objects.select_for_update().filter(expires_date__lt=reference_date)
        for reservation in reservations:
            book_copy = BookCopy.objects.select_for_update().get(pk=reservation.book_copy_id)
            if book_copy.status != BookCopy.Status.RESERVED:
                continue

            reservation.delete()
            released_count += 1

            book_copy.status = BookCopy.Status.AVAILABLE
            book_copy.save(update_fields=["status", "updated_at"])

    return released_count


def create_reservation(user: AppUser, book_id: UUID, scheduled_date) -> Reservation:
    try:
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
                raise ActionConflictError("予約可能な蔵書がありません")

            reservation = Reservation.objects.create(
                book_copy=book_copy,
                user=user,
                scheduled_date=scheduled_date,
                expires_date=scheduled_date + timedelta(days=DEFAULT_RESERVATION_HOLD_DAYS - 1),
            )
            book_copy.status = BookCopy.Status.RESERVED
            book_copy.save(update_fields=["status", "updated_at"])
    except IntegrityError as error:
        raise ActionConflictError("この蔵書はすでに予約されています") from error

    return reservation


def cancel_reservation(user: AppUser, reservation_id: UUID) -> None:
    with transaction.atomic():
        reservation = _get_locked_reservation(reservation_id)
        _ensure_reservation_owner(reservation, user)

        book_copy = BookCopy.objects.select_for_update().get(pk=reservation.book_copy_id)

        reservation.delete()

        if book_copy.status == BookCopy.Status.RESERVED:
            book_copy.status = BookCopy.Status.AVAILABLE
            book_copy.save(update_fields=["status", "updated_at"])


def convert_reservation_to_lending(user: AppUser, reservation_id: UUID) -> Lending:
    try:
        with transaction.atomic():
            reservation = _get_locked_reservation(reservation_id)
            _ensure_reservation_owner(reservation, user)

            today = timezone.localdate()
            if today < reservation.scheduled_date:
                raise ActionConflictError("予約日より前には貸出に変換できません")
            if today > reservation.expires_date:
                raise ActionConflictError("取り置き期限を過ぎています")

            book_copy = reservation.book_copy
            if book_copy.status != BookCopy.Status.RESERVED:
                raise ActionConflictError("予約中の蔵書ではありません")

            borrowed_date = today
            lending = Lending.objects.create(
                book_copy=book_copy,
                user=user,
                borrowed_date=borrowed_date,
                due_date=borrowed_date + timedelta(days=DEFAULT_LENDING_DAYS - 1),
            )
            book_copy.status = BookCopy.Status.ON_LOAN
            book_copy.save(update_fields=["status", "updated_at"])
            reservation.delete()
    except IntegrityError as error:
        raise ActionConflictError("貸出状態が競合しました") from error

    return lending


def list_current_reservations(user: AppUser):
    return (
        Reservation.objects.select_related("book_copy", "book_copy__book")
        .filter(user=user)
        .order_by("scheduled_date", "created_at")
    )


def _get_locked_reservation(reservation_id: UUID) -> Reservation:
    try:
        return Reservation.objects.select_for_update().select_related("book_copy").get(pk=reservation_id)
    except Reservation.DoesNotExist as error:
        raise ReservationNotFoundError("予約が見つかりません") from error


def _ensure_reservation_owner(reservation: Reservation, user: AppUser) -> None:
    if reservation.user_id != user.id:
        raise PermissionDenied("この予約を操作する権限がありません")
