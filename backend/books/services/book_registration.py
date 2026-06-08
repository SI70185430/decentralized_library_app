from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from django.core.exceptions import ValidationError
from django.db import transaction

from books.models import Book, BookCopy, Genre
from books.services.openbd import normalize_isbn13

COPY_COUNT_ERROR_MESSAGE = "冊数は1以上で入力してください"
LOCATION_ERROR_MESSAGE = "保管場所を入力してください"
TITLE_ERROR_MESSAGE = "タイトルを入力してください"


@dataclass(frozen=True)
class BookRegistrationResult:
    book: Book
    book_created: bool
    copies: list[BookCopy]


def register_book_copies(data: Mapping[str, Any]) -> BookRegistrationResult:
    """Create a Book when needed and add the requested number of BookCopy rows."""
    isbn = normalize_isbn13(data.get("isbn", ""))
    copy_count = _normalize_copy_count(data.get("copy_count"))
    location = _normalize_required_string(data.get("location"), LOCATION_ERROR_MESSAGE)
    title = _normalize_required_string(data.get("title"), TITLE_ERROR_MESSAGE)
    genre = _get_genre(data.get("genre_code"))

    with transaction.atomic():
        book, book_created = Book.objects.get_or_create(
            isbn=isbn,
            defaults={
                "genre": genre,
                "title": title,
                "author": data.get("author") or "",
                "publisher": data.get("publisher") or "",
                "published_date": data.get("published_date") or None,
                "price": data.get("price"),
                "cover_image_url": data.get("cover_image_url") or "",
            },
        )

        copies = BookCopy.objects.bulk_create(
            [
                BookCopy(
                    book=book,
                    status=BookCopy.Status.AVAILABLE,
                    location=location,
                    purchase_date=data.get("purchase_date") or None,
                )
                for _ in range(copy_count)
            ]
        )

    return BookRegistrationResult(book=book, book_created=book_created, copies=copies)


def _normalize_copy_count(value: Any) -> int:
    try:
        copy_count = int(value)
    except (TypeError, ValueError) as error:
        raise ValidationError(COPY_COUNT_ERROR_MESSAGE) from error

    if copy_count < 1:
        raise ValidationError(COPY_COUNT_ERROR_MESSAGE)

    return copy_count


def _normalize_required_string(value: Any, error_message: str) -> str:
    normalized = str(value or "").strip()
    if not normalized:
        raise ValidationError(error_message)
    return normalized


def _get_genre(genre_code: Any) -> Genre | None:
    if not genre_code:
        return None

    return Genre.objects.get(c_code_genre=genre_code)
