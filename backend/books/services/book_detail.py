from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING
from uuid import UUID

from books.models import BookCopy
from lending.models import Lending

if TYPE_CHECKING:
    from accounts.models import AppUser
    from books.models import Book


@dataclass(frozen=True)
class BookAvailability:
    status_code: str
    status_label: str
    available_copy_count: int
    current_lending_id: UUID | None


@dataclass(frozen=True)
class BookAction:
    type: str
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


def build_book_detail_state(book: Book, user: AppUser) -> BookDetailState:
    current_lending = (
        Lending.objects.select_related("book_copy")
        .filter(user=user, book_copy__book=book, returned_date__isnull=True)
        .first()
    )
    available_copy_count = BookCopy.objects.filter(
        book=book,
        status=BookCopy.Status.AVAILABLE,
    ).count()

    if current_lending is not None:
        return _build_using_state(current_lending.id, available_copy_count)

    if available_copy_count > 0:
        return _build_available_state(book.id, available_copy_count)

    if BookCopy.objects.filter(book=book, status=BookCopy.Status.ON_LOAN).exists():
        return BookDetailState(
            availability=BookAvailability(
                status_code="on_loan",
                status_label="貸出中",
                available_copy_count=0,
                current_lending_id=None,
            ),
            primary_action=None,
            secondary_action=None,
        )

    return BookDetailState(
        availability=BookAvailability(
            status_code="unavailable",
            status_label="貸出不可",
            available_copy_count=0,
            current_lending_id=None,
        ),
        primary_action=None,
        secondary_action=None,
    )


def _build_using_state(
    lending_id: UUID,
    available_copy_count: int,
) -> BookDetailState:
    return BookDetailState(
        availability=BookAvailability(
            status_code="using",
            status_label="利用中",
            available_copy_count=available_copy_count,
            current_lending_id=lending_id,
        ),
        primary_action=BookAction(
            type="return",
            label="この本を返却する",
            method="POST",
            endpoint="/api/lendings/{lending_id}/return/",
            request_body={},
            enabled=True,
        ),
        secondary_action=BookAction(
            type="extend",
            label="期限延長",
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
            status_code="available",
            status_label="貸出可",
            available_copy_count=available_copy_count,
            current_lending_id=None,
        ),
        primary_action=BookAction(
            type="borrow",
            label="この本を借りる",
            method="POST",
            endpoint="/api/lendings/",
            request_body={"book_id": str(book_id)},
            enabled=True,
        ),
        secondary_action=None,
    )
