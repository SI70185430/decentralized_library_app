from django.test import TestCase
from django.urls import reverse

from books.forms import BookRegisterForm
from books.models import Book, BookCopy
from books.tests.helpers import (
    DEFAULT_LOCATION,
    DEFAULT_TITLE,
    INVALID_ISBN,
    VALID_ISBN,
    VALID_ISBN10,
    book_register_form_data,
    create_genre,
    create_staff_user,
)


class BookRegisterAdminViewTests(TestCase):
    def setUp(self):
        self.staff_user = create_staff_user(username="book-admin", employee_id=700001)

    def test_register_view_requires_staff_login(self):
        response = self.client.get(reverse("admin_books_register"))

        self.assertEqual(response.status_code, 302)
        self.assertIn("/admin/login/", response["Location"])

    def test_register_view_renders_form_for_staff_user(self):
        self.client.force_login(self.staff_user)

        response = self.client.get(reverse("admin_books_register"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "admin/books/register.html")
        self.assertContains(response, "書籍登録")
        self.assertContains(response, "ISBNコード")
        self.assertContains(response, 'id="btn_isbn_scan"')
        self.assertContains(response, 'id="btn_book_info"')
        self.assertContains(response, "書籍情報取得")
        self.assertContains(response, 'class="book-register-shell"')
        self.assertContains(response, 'class="book-register-panel"')
        self.assertContains(response, 'class="book-register-two-column"')
        self.assertContains(response, 'class="book-register-primary-action"')
        self.assertContains(response, 'class="book-register-sr-label"')
        self.assertIsInstance(response.context["form"], BookRegisterForm)

    def test_register_view_posts_valid_data_and_creates_copies(self):
        self.client.force_login(self.staff_user)
        genre = create_genre()

        response = self.client.post(
            reverse("admin_books_register"),
            data=book_register_form_data(
                genre_code=genre.c_code_genre,
                copy_count="2",
            ),
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], reverse("admin_books_register"))
        book = Book.objects.get(isbn=VALID_ISBN)
        self.assertEqual(book.title, DEFAULT_TITLE)
        self.assertEqual(BookCopy.objects.filter(book=book, location=DEFAULT_LOCATION).count(), 2)

    def test_register_view_posts_isbn10_and_saves_isbn13(self):
        self.client.force_login(self.staff_user)

        response = self.client.post(
            reverse("admin_books_register"),
            data=book_register_form_data(isbn=VALID_ISBN10),
        )

        self.assertEqual(response.status_code, 302)
        book = Book.objects.get(isbn=VALID_ISBN)
        self.assertEqual(book.title, DEFAULT_TITLE)
        self.assertEqual(BookCopy.objects.filter(book=book, location=DEFAULT_LOCATION).count(), 1)

    def test_register_view_keeps_form_errors_without_creating_rows(self):
        self.client.force_login(self.staff_user)

        response = self.client.post(
            reverse("admin_books_register"),
            data=book_register_form_data(
                isbn=INVALID_ISBN,
                author="",
                publisher="",
                published_date="",
                cover_image_url="",
                price="",
                genre_code="",
                purchase_date="",
            ),
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "admin/books/register.html")
        self.assertContains(response, "10桁または13桁のISBNを入力してください")
        self.assertEqual(Book.objects.count(), 0)
        self.assertEqual(BookCopy.objects.count(), 0)


class BookRegisterAdminNavigationTests(TestCase):
    def setUp(self):
        self.staff_user = create_staff_user(
            username="book-navigation-admin",
            employee_id=700003,
        )

    def test_admin_header_links_to_book_register_view(self):
        self.client.force_login(self.staff_user)

        response = self.client.get(reverse("admin:index"))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "書籍管理")
        self.assertContains(response, "書籍登録", count=1)
        self.assertContains(response, f'href="{reverse("admin_books_register")}"', count=1)
        self.assertContains(response, 'href="/static/books/admin/jazzmin.css"')
