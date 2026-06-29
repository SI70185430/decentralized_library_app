from dataclasses import dataclass
from uuid import UUID

from django.db import models

from accounts.models import AppUser
from books.models import Book, BookCopy
from lending.models import Lending, Reservation


class BookAvailabilityStatus(models.TextChoices):
    USING = "using", "利用中"
    AVAILABLE = "available", "貸出可"
    HOLD = "hold", "取り置き中"
    ON_LOAN = "on_loan", "貸出中"
    UNAVAILABLE = "unavailable", "貸出不可"


class BookActionType(models.TextChoices):
    BORROW = "borrow", "この本を借りる"
    RETURN = "return", "この本を返却する"
    EXTEND = "extend", "期限延長"
    CHANGE_HOLD = "change_hold", "予約変更"
    CANCEL_HOLD = "cancel_hold", "キャンセル"


@dataclass(frozen=True)
class BookAvailability:
    status_code: BookAvailabilityStatus
    current_lending_id: UUID | None
    current_reservation_id: UUID | None


@dataclass(frozen=True)
class BookAction:
    type: BookActionType


@dataclass(frozen=True)
class BookDetailState:
    availability: BookAvailability
    primary_action: BookAction | None
    secondary_action: BookAction | None


def build_book_detail_state(book: Book, user: AppUser | None = None) -> BookDetailState:
    current_lending = None
    current_reservation = None
    if user is not None and user.is_authenticated:
        current_lending = Lending.objects.filter(
            user=user,
            book_copy__book=book,
            returned_date__isnull=True,
        ).first()
        current_reservation = Reservation.objects.filter(
            user=user,
            book_copy__book=book,
        ).first()

    if current_lending is not None:
        return _build_using_state(current_lending.id)

    if current_reservation is not None:
        return _build_my_hold_state(current_reservation.id)

    available_copy_count = BookCopy.objects.filter(
        book=book,
        status=BookCopy.Status.AVAILABLE,
    ).count()
    if available_copy_count == 0:
        return _build_on_loan_state()

    return _build_available_state()


def _build_using_state(lending_id: UUID) -> BookDetailState:
    return BookDetailState(
        availability=BookAvailability(
            status_code=BookAvailabilityStatus.USING,
            current_lending_id=lending_id,
            current_reservation_id=None,
        ),
        primary_action=BookAction(type=BookActionType.RETURN),
        secondary_action=BookAction(type=BookActionType.EXTEND),
    )


def _build_available_state() -> BookDetailState:
    return BookDetailState(
        availability=BookAvailability(
            status_code=BookAvailabilityStatus.AVAILABLE,
            current_lending_id=None,
            current_reservation_id=None,
        ),
        primary_action=BookAction(type=BookActionType.BORROW),
        secondary_action=None,
    )


def _build_my_hold_state(reservation_id: UUID) -> BookDetailState:
    return BookDetailState(
        availability=BookAvailability(
            status_code=BookAvailabilityStatus.HOLD,
            current_lending_id=None,
            current_reservation_id=reservation_id,
        ),
        primary_action=BookAction(type=BookActionType.CHANGE_HOLD),
        secondary_action=BookAction(type=BookActionType.CANCEL_HOLD),
    )


def _build_on_loan_state() -> BookDetailState:
    return BookDetailState(
        availability=BookAvailability(
            status_code=BookAvailabilityStatus.ON_LOAN,
            current_lending_id=None,
            current_reservation_id=None,
        ),
        primary_action=None,
        secondary_action=None,
    )
