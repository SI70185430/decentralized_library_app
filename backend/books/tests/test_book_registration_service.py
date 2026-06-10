from django.db import connection
from django.test import TestCase
from django.test.utils import CaptureQueriesContext

from books.models import Book, BookCopy
from books.services.book_registration import register_book_copies
from books.tests.helpers import (
    DEFAULT_LOCATION,
    DEFAULT_PURCHASE_DATE,
    VALID_ISBN,
    book_registration_cleaned_data,
    create_book,
    create_genre,
)


class BookRegistrationServiceTests(TestCase):
    def test_register_book_copies_creates_new_book_and_requested_copies(self):
        genre = create_genre()

        result = register_book_copies(
            book_registration_cleaned_data(
                genre_code=genre.c_code_genre,
                copy_count=3,
            )
        )

        book = Book.objects.get(isbn=VALID_ISBN)
        copies = BookCopy.objects.filter(book=book).order_by("created_at")

        self.assertEqual(result.book, book)
        self.assertEqual(result.book_created, True)
        self.assertEqual(len(result.copies), 3)
        self.assertEqual(copies.count(), 3)
        self.assertEqual(book.genre_id, "55")
        self.assertEqual(book.title, "新規書籍")
        self.assertEqual(book.author, "新規著者")
        self.assertEqual(book.publisher, "新規出版社")
        self.assertEqual(book.published_date, book_registration_cleaned_data()["published_date"])
        self.assertEqual(book.price, 1200)
        self.assertEqual(book.cover_image_url, "https://example.com/new.jpg")
        self.assertTrue(
            all(copy.status == BookCopy.Status.AVAILABLE for copy in copies),
        )
        self.assertTrue(all(copy.location == DEFAULT_LOCATION for copy in copies))
        self.assertTrue(all(copy.purchase_date == DEFAULT_PURCHASE_DATE for copy in copies))

    def test_register_book_copies_uses_existing_book_without_updating_it(self):
        existing_book = create_book(
            title="既存タイトル",
            author="既存著者",
            publisher=None,
        )

        result = register_book_copies(
            book_registration_cleaned_data(
                title="更新してはいけないタイトル",
                author="更新してはいけない著者",
                publisher="更新してはいけない出版社",
                genre_code="",
                purchase_date=None,
                location="2F-B-02",
                copy_count=2,
            )
        )

        existing_book.refresh_from_db()

        self.assertEqual(result.book, existing_book)
        self.assertEqual(result.book_created, False)
        self.assertEqual(len(result.copies), 2)
        self.assertEqual(Book.objects.count(), 1)
        self.assertEqual(BookCopy.objects.filter(book=existing_book).count(), 2)
        self.assertEqual(existing_book.title, "既存タイトル")
        self.assertEqual(existing_book.author, "既存著者")
        self.assertEqual(existing_book.publisher, None)

    def test_register_book_copies_uses_cleaned_genre_code_without_genre_lookup(self):
        genre = create_genre()

        with CaptureQueriesContext(connection) as captured_queries:
            result = register_book_copies(
                book_registration_cleaned_data(genre_code=genre.c_code_genre)
            )

        genre_select_queries = [
            query["sql"]
            for query in captured_queries
            if 'FROM "genre"' in query["sql"] or 'FROM "books_genre"' in query["sql"]
        ]
        self.assertEqual(result.book.genre_id, genre.c_code_genre)
        self.assertEqual(genre_select_queries, [])

    def test_register_book_copies_requires_cleaned_data_shape(self):
        with self.assertRaises(KeyError):
            register_book_copies(
                {
                    "isbn": VALID_ISBN,
                    "title": "新規書籍",
                    "location": DEFAULT_LOCATION,
                    "copy_count": 1,
                }
            )
