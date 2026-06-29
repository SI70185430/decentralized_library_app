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
    status_label: str
    available_copy_count: int
    current_lending_id: UUID | None
    current_reservation_id: UUID | None


@dataclass(frozen=True)
class BookAction:
    type: BookActionType
    label: str
    method: str
    endpoint: str
    request_body: dict[str, str]
    enabled: bool


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

    available_copy_count = BookCopy.objects.filter(
        book=book,
        status=BookCopy.Status.AVAILABLE,
    ).count()

    if current_lending is not None:
        return _build_using_state(current_lending.id, available_copy_count)

    if current_reservation is not None:
        return _build_my_hold_state(book.id, current_reservation.id, available_copy_count)

    if available_copy_count == 0:
        return _build_on_loan_state()

    return _build_available_state(book.id, available_copy_count)


def _build_using_state(
    lending_id: UUID,
    available_copy_count: int,
) -> BookDetailState:
    return BookDetailState(
        availability=BookAvailability(
            status_code=BookAvailabilityStatus.USING,
            status_label=BookAvailabilityStatus.USING.label,
            available_copy_count=available_copy_count,
            current_lending_id=lending_id,
            current_reservation_id=None,
        ),
        primary_action=BookAction(
            type=BookActionType.RETURN,
            label=BookActionType.RETURN.label,
            method="POST",
            endpoint="/api/lendings/{lending_id}/return/",
            request_body={},
            enabled=True,
        ),
        secondary_action=BookAction(
            type=BookActionType.EXTEND,
            label=BookActionType.EXTEND.label,
            method="POST",
            endpoint="/api/lendings/{lending_id}/extend/",
            request_body={},
            enabled=True,
        ),
    )


def _build_available_state(
    book_id: UUID,
    available_copy_count: int,
) -> BookDetailState:
    return BookDetailState(
        availability=BookAvailability(
            status_code=BookAvailabilityStatus.AVAILABLE,
            status_label=BookAvailabilityStatus.AVAILABLE.label,
            available_copy_count=available_copy_count,
            current_lending_id=None,
            current_reservation_id=None,
        ),
        primary_action=BookAction(
            type=BookActionType.BORROW,
            label=BookActionType.BORROW.label,
            method="POST",
            endpoint="/api/lendings/",
            request_body={"book_id": str(book_id)},
            enabled=True,
        ),
        secondary_action=None,
    )


def _build_my_hold_state(
    book_id: UUID,
    reservation_id: UUID,
    available_copy_count: int,
) -> BookDetailState:
    return BookDetailState(
        availability=BookAvailability(
            status_code=BookAvailabilityStatus.HOLD,
            status_label=BookAvailabilityStatus.HOLD.label,
            available_copy_count=available_copy_count,
            current_lending_id=None,
            current_reservation_id=reservation_id,
        ),
        primary_action=BookAction(
            type=BookActionType.CHANGE_HOLD,
            label=BookActionType.CHANGE_HOLD.label,
            method="POST",
            endpoint="/api/reservations/",
            request_body={"book_id": str(book_id), "scheduled_date": "YYYY-MM-DD"},
            enabled=True,
        ),
        secondary_action=BookAction(
            type=BookActionType.CANCEL_HOLD,
            label=BookActionType.CANCEL_HOLD.label,
            method="POST",
            endpoint="/api/reservations/{reservation_id}/cancel/",
            request_body={},
            enabled=True,
        ),
    )


def _build_on_loan_state() -> BookDetailState:
    return BookDetailState(
        availability=BookAvailability(
            status_code=BookAvailabilityStatus.ON_LOAN,
            status_label=BookAvailabilityStatus.ON_LOAN.label,
            available_copy_count=0,
            current_lending_id=None,
            current_reservation_id=None,
        ),
        primary_action=None,
        secondary_action=None,
    )
