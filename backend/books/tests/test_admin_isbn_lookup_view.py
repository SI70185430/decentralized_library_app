from datetime import date
from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse

from books.services.openbd import OpenBdError
from books.tests.helpers import (
    INVALID_ISBN,
    INVALID_ISBN10_CHECK_DIGIT,
    INVALID_ISBN13_CHECK_DIGIT,
    VALID_ISBN,
    VALID_ISBN10,
    VALID_ISBN_WITH_HYPHENS,
    create_book,
    create_genre,
    create_staff_user,
)


class BookIsbnLookupAdminViewTests(TestCase):
    def setUp(self):
        self.staff_user = create_staff_user(username="book-lookup-admin", employee_id=700002)

    def test_isbn_lookup_requires_staff_login(self):
        response = self.client.get(reverse("admin_books_isbn_lookup"), {"isbn": VALID_ISBN})

        self.assertEqual(response.status_code, 302)
        self.assertIn("/admin/login/", response["Location"])

    def test_isbn_lookup_returns_existing_book_data_as_json(self):
        self.client.force_login(self.staff_user)
        genre = create_genre(code="41", name="数学")
        create_book(
            genre=genre,
            title="既存書籍",
            author="既存著者",
            publisher="既存出版社",
            published_date=date(1990, 4, 1),
            price=1200,
            cover_image_url="https://example.com/existing.jpg",
        )

        response = self.client.get(
            reverse("admin_books_isbn_lookup"), {"isbn": VALID_ISBN_WITH_HYPHENS}
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "book": {
                    "isbn": VALID_ISBN,
                    "title": "既存書籍",
                    "author": "既存著者",
                    "publisher": "既存出版社",
                    "published_date": "1990-04-01",
                    "cover_image_url": "https://example.com/existing.jpg",
                    "price": 1200,
                    "genre_code": "41",
                }
            },
        )

    def test_isbn_lookup_returns_existing_book_data_from_isbn10_as_json(self):
        self.client.force_login(self.staff_user)
        create_book(title="既存書籍", author="既存著者")

        response = self.client.get(reverse("admin_books_isbn_lookup"), {"isbn": VALID_ISBN10})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["book"]["isbn"], VALID_ISBN)
        self.assertEqual(response.json()["book"]["title"], "既存書籍")
        self.assertEqual(response.json()["book"]["author"], "既存著者")

    def test_isbn_lookup_returns_400_for_invalid_isbn(self):
        self.client.force_login(self.staff_user)

        response = self.client.get(reverse("admin_books_isbn_lookup"), {"isbn": INVALID_ISBN})

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"error": "10桁または13桁で正当なISBNを入力してください"})

    def test_isbn_lookup_returns_400_for_isbn10_with_invalid_check_digit(self):
        self.client.force_login(self.staff_user)

        response = self.client.get(
            reverse("admin_books_isbn_lookup"), {"isbn": INVALID_ISBN10_CHECK_DIGIT}
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"error": "10桁または13桁で正当なISBNを入力してください"})

    def test_isbn_lookup_returns_400_for_isbn13_with_invalid_check_digit(self):
        self.client.force_login(self.staff_user)

        response = self.client.get(
            reverse("admin_books_isbn_lookup"), {"isbn": INVALID_ISBN13_CHECK_DIGIT}
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"error": "10桁または13桁で正当なISBNを入力してください"})

    def test_isbn_lookup_returns_404_when_book_is_not_found(self):
        self.client.force_login(self.staff_user)

        with patch("books.services.openbd.fetch_openbd_book_data", return_value=None):
            response = self.client.get(reverse("admin_books_isbn_lookup"), {"isbn": VALID_ISBN})

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"error": "書籍情報が見つかりませんでした"})

    def test_isbn_lookup_returns_502_when_openbd_fails(self):
        self.client.force_login(self.staff_user)

        with patch(
            "books.services.openbd.fetch_openbd_book_data", side_effect=OpenBdError("timeout")
        ):
            response = self.client.get(reverse("admin_books_isbn_lookup"), {"isbn": VALID_ISBN})

        self.assertEqual(response.status_code, 502)
        self.assertEqual(response.json(), {"error": "openBDから書籍情報を取得できませんでした"})
