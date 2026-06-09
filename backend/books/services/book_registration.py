from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from django.db import transaction

from books.models import Book, BookCopy


@dataclass(frozen=True)
class BookRegistrationResult:
    book: Book
    book_created: bool
    copies: list[BookCopy]


def register_book_copies(cleaned_data: Mapping[str, Any]) -> BookRegistrationResult:
    """Create a Book and BookCopy rows from BookRegisterForm.cleaned_data."""
    isbn = cleaned_data["isbn"]
    title = cleaned_data["title"]
    author = cleaned_data["author"]
    publisher = cleaned_data["publisher"]
    published_date = cleaned_data["published_date"]
    price = cleaned_data["price"]
    cover_image_url = cleaned_data["cover_image_url"]
    genre_id = cleaned_data["genre_code"] or None
    purchase_date = cleaned_data["purchase_date"]
    location = cleaned_data["location"]
    copy_count = cleaned_data["copy_count"]

    with transaction.atomic():
        book, book_created = Book.objects.get_or_create(
            isbn=isbn,
            defaults={
                "genre_id": genre_id,
                "title": title,
                "author": author,
                "publisher": publisher,
                "published_date": published_date,
                "price": price,
                "cover_image_url": cover_image_url,
            },
        )

        copies = BookCopy.objects.bulk_create(
            [
                BookCopy(
                    book=book,
                    location=location,
                    purchase_date=purchase_date,
                )
                for _ in range(copy_count)
            ]
        )

    return BookRegistrationResult(book=book, book_created=book_created, copies=copies)
