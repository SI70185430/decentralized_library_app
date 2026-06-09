import json
import urllib.error
from datetime import date
from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import connection
from django.test import TestCase
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

from books.forms import BookRegisterForm
from books.models import Book, BookCopy, Genre
from books.services.book_registration import register_book_copies
from books.services.openbd import (
    OpenBdError,
    book_to_lookup_data,
    fetch_openbd_book_data,
    lookup_book_info_by_isbn,
    map_openbd_book_data,
    normalize_isbn13,
    parse_openbd_pubdate,
)


class IsbnHelperTests(TestCase):
    def test_normalize_isbn13_removes_hyphens_and_spaces(self):
        self.assertEqual(normalize_isbn13(" 978-4-00-310101-8 "), "9784003101018")

    def test_normalize_isbn13_rejects_non_13_digits(self):
        invalid_values = ["", "978400310101", "97840031010180", "978400310101X", "4003101014"]

        for value in invalid_values:
            with self.subTest(value=value), self.assertRaises(ValidationError):
                normalize_isbn13(value)


class OpenBdPubdateHelperTests(TestCase):
    def test_parse_openbd_pubdate_with_year(self):
        self.assertEqual(parse_openbd_pubdate("1990"), date(1990, 1, 1))

    def test_parse_openbd_pubdate_with_year_month(self):
        self.assertEqual(parse_openbd_pubdate("199004"), date(1990, 4, 1))

    def test_parse_openbd_pubdate_with_year_month_day(self):
        self.assertEqual(parse_openbd_pubdate("19900410"), date(1990, 4, 10))

    def test_parse_openbd_pubdate_returns_none_for_invalid_value(self):
        invalid_values = [None, "", "1990-04", "unknown", "199013", "19900230"]

        for value in invalid_values:
            with self.subTest(value=value):
                self.assertIsNone(parse_openbd_pubdate(value))


class OpenBdClientTests(TestCase):
    def test_fetch_openbd_book_data_returns_full_openbd_data(self):
        openbd_data = {
            "summary": {"isbn": "9784003101018", "title": "吾輩は猫である"},
            "onix": {"ProductSupply": {"SupplyDetail": {"Price": {"PriceAmount": "1200"}}}},
        }
        response = Mock()
        response.__enter__ = Mock(return_value=response)
        response.__exit__ = Mock(return_value=None)
        response.read.return_value = json.dumps([openbd_data]).encode()

        with patch("books.services.openbd.urllib.request.urlopen", return_value=response):
            result = fetch_openbd_book_data("9784003101018")

        self.assertEqual(result, openbd_data)

    def test_fetch_openbd_book_data_returns_none_when_summary_is_not_dict(self):
        response = Mock()
        response.__enter__ = Mock(return_value=response)
        response.__exit__ = Mock(return_value=None)
        response.read.return_value = json.dumps([{"summary": "invalid"}]).encode()

        with patch("books.services.openbd.urllib.request.urlopen", return_value=response):
            result = fetch_openbd_book_data("9784003101018")

        self.assertIsNone(result)

    def test_fetch_openbd_book_data_returns_none_when_summary_is_empty(self):
        response = Mock()
        response.__enter__ = Mock(return_value=response)
        response.__exit__ = Mock(return_value=None)
        response.read.return_value = json.dumps([{"summary": {}}]).encode()

        with patch("books.services.openbd.urllib.request.urlopen", return_value=response):
            result = fetch_openbd_book_data("9784003101018")

        self.assertIsNone(result)

    def test_fetch_openbd_book_data_raises_openbd_error_on_network_error(self):
        with (
            patch(
                "books.services.openbd.urllib.request.urlopen",
                side_effect=urllib.error.URLError("timeout"),
            ),
            self.assertRaises(OpenBdError),
        ):
            fetch_openbd_book_data("9784003101018")


class OpenBdMappingTests(TestCase):
    def test_map_openbd_book_data_maps_fields_from_summary_and_onix(self):
        result = map_openbd_book_data(
            {
                "summary": {
                    "title": "吾輩は猫である",
                    "author": "夏目漱石",
                    "publisher": "岩波書店",
                    "pubdate": "199004",
                    "cover": "https://example.com/cover.jpg",
                },
                "onix": {
                    "ProductSupply": {
                        "SupplyDetail": {
                            "Price": [{"PriceAmount": "1,200円"}],
                        }
                    },
                },
            },
            "9784003101018",
        )

        self.assertEqual(
            result,
            {
                "isbn": "9784003101018",
                "title": "吾輩は猫である",
                "author": "夏目漱石",
                "publisher": "岩波書店",
                "published_date": date(1990, 4, 1),
                "cover_image_url": "https://example.com/cover.jpg",
                "price": 1200,
                "genre_code": "",
            },
        )

    def test_book_to_lookup_data_maps_existing_book(self):
        genre = Genre.objects.create(c_code_genre="41", name="数学")
        book = Book.objects.create(
            genre=genre,
            isbn="9784003101018",
            title="既存書籍",
            author="既存著者",
            publisher="既存出版社",
            published_date=date(1990, 4, 1),
            price=1200,
            cover_image_url="https://example.com/existing.jpg",
        )

        self.assertEqual(
            book_to_lookup_data(book),
            {
                "isbn": "9784003101018",
                "title": "既存書籍",
                "author": "既存著者",
                "publisher": "既存出版社",
                "published_date": date(1990, 4, 1),
                "cover_image_url": "https://example.com/existing.jpg",
                "price": 1200,
                "genre_code": "41",
            },
        )


class BookInfoLookupTests(TestCase):
    def test_lookup_book_info_by_isbn_returns_existing_book_without_openbd_call(self):
        Book.objects.create(
            isbn="9784003101018",
            title="既存書籍",
            author="既存著者",
        )

        with patch("books.services.openbd.fetch_openbd_book_data") as fetch_openbd_book_data_mock:
            result = lookup_book_info_by_isbn("978-4-00-310101-8")

        fetch_openbd_book_data_mock.assert_not_called()
        self.assertEqual(result["isbn"], "9784003101018")
        self.assertEqual(result["title"], "既存書籍")
        self.assertEqual(result["author"], "既存著者")

    def test_lookup_book_info_by_isbn_fetches_openbd_when_book_does_not_exist(self):
        with patch(
            "books.services.openbd.fetch_openbd_book_data",
            return_value={
                "summary": {
                    "isbn": "9784003101018",
                    "title": "吾輩は猫である",
                    "pubdate": "19900410",
                }
            },
        ) as fetch_openbd_book_data_mock:
            result = lookup_book_info_by_isbn("978-4-00-310101-8")

        fetch_openbd_book_data_mock.assert_called_once_with("9784003101018")
        self.assertEqual(result["isbn"], "9784003101018")
        self.assertEqual(result["title"], "吾輩は猫である")
        self.assertEqual(result["published_date"], date(1990, 4, 10))

    def test_lookup_book_info_by_isbn_returns_none_when_openbd_has_no_data(self):
        with patch("books.services.openbd.fetch_openbd_book_data", return_value=None):
            result = lookup_book_info_by_isbn("978-4-00-310101-8")

        self.assertIsNone(result)


class BookRegistrationServiceTests(TestCase):
    def test_register_book_copies_creates_new_book_and_requested_copies(self):
        genre = Genre.objects.create(c_code_genre="55", name="電気通信")

        result = register_book_copies(
            {
                "isbn": "9784003101018",
                "title": "新規書籍",
                "author": "新規著者",
                "publisher": "新規出版社",
                "published_date": date(1990, 4, 1),
                "price": 1200,
                "cover_image_url": "https://example.com/new.jpg",
                "genre_code": genre.c_code_genre,
                "purchase_date": date(2026, 6, 7),
                "location": "1F-A-01",
                "copy_count": 3,
            }
        )

        book = Book.objects.get(isbn="9784003101018")
        copies = BookCopy.objects.filter(book=book).order_by("created_at")

        self.assertEqual(result.book, book)
        self.assertEqual(result.book_created, True)
        self.assertEqual(len(result.copies), 3)
        self.assertEqual(copies.count(), 3)
        self.assertEqual(book.genre_id, "55")
        self.assertEqual(book.title, "新規書籍")
        self.assertEqual(book.author, "新規著者")
        self.assertEqual(book.publisher, "新規出版社")
        self.assertEqual(book.published_date, date(1990, 4, 1))
        self.assertEqual(book.price, 1200)
        self.assertEqual(book.cover_image_url, "https://example.com/new.jpg")
        self.assertTrue(
            all(copy.status == BookCopy.Status.AVAILABLE for copy in copies),
        )
        self.assertTrue(all(copy.location == "1F-A-01" for copy in copies))
        self.assertTrue(all(copy.purchase_date == date(2026, 6, 7) for copy in copies))

    def test_register_book_copies_uses_existing_book_without_updating_it(self):
        existing_book = Book.objects.create(
            isbn="9784003101018",
            title="既存タイトル",
            author="既存著者",
        )

        result = register_book_copies(
            {
                "isbn": "9784003101018",
                "title": "更新してはいけないタイトル",
                "author": "更新してはいけない著者",
                "publisher": "更新してはいけない出版社",
                "published_date": date(1990, 4, 1),
                "price": 1200,
                "cover_image_url": "https://example.com/new.jpg",
                "genre_code": "",
                "purchase_date": None,
                "location": "2F-B-02",
                "copy_count": 2,
            }
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
        genre = Genre.objects.create(c_code_genre="55", name="電気通信")

        with CaptureQueriesContext(connection) as captured_queries:
            result = register_book_copies(
                {
                    "isbn": "9784003101018",
                    "title": "新規書籍",
                    "author": "新規著者",
                    "publisher": "新規出版社",
                    "published_date": date(1990, 4, 1),
                    "price": 1200,
                    "cover_image_url": "https://example.com/new.jpg",
                    "genre_code": genre.c_code_genre,
                    "purchase_date": date(2026, 6, 7),
                    "location": "1F-A-01",
                    "copy_count": 1,
                }
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
                    "isbn": "9784003101018",
                    "title": "新規書籍",
                    "location": "1F-A-01",
                    "copy_count": 1,
                }
            )


class BookRegisterAdminViewTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.staff_user = User.objects.create_user(
            username="book-admin",
            employee_id=700001,
            password="password123",
            is_staff=True,
        )

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
        genre = Genre.objects.create(c_code_genre="55", name="電気通信")

        response = self.client.post(
            reverse("admin_books_register"),
            data={
                "isbn": "978-4-00-310101-8",
                "title": "吾輩は猫である",
                "author": "夏目漱石",
                "publisher": "岩波書店",
                "published_date": "1990-04-01",
                "cover_image_url": "https://example.com/cover.jpg",
                "price": "1200",
                "genre_code": genre.c_code_genre,
                "purchase_date": "2026-06-07",
                "location": "1F-A-01",
                "copy_count": "2",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], reverse("admin_books_register"))
        book = Book.objects.get(isbn="9784003101018")
        self.assertEqual(book.title, "吾輩は猫である")
        self.assertEqual(BookCopy.objects.filter(book=book, location="1F-A-01").count(), 2)

    def test_register_view_keeps_form_errors_without_creating_rows(self):
        self.client.force_login(self.staff_user)

        response = self.client.post(
            reverse("admin_books_register"),
            data={
                "isbn": "4003101014",
                "title": "吾輩は猫である",
                "location": "1F-A-01",
                "copy_count": "1",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "admin/books/register.html")
        self.assertContains(response, "ISBNは13桁で入力してください")
        self.assertEqual(Book.objects.count(), 0)
        self.assertEqual(BookCopy.objects.count(), 0)


class BookRegisterAdminNavigationTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.staff_user = User.objects.create_user(
            username="book-navigation-admin",
            employee_id=700003,
            password="password123",
            is_staff=True,
        )

    def test_admin_dashboard_links_to_book_register_view(self):
        self.client.force_login(self.staff_user)

        response = self.client.get(reverse("admin:index"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "書籍管理")
        self.assertContains(response, "書籍登録", count=2)
        self.assertContains(response, f'href="{reverse("admin_books_register")}"', count=3)


class BookIsbnLookupAdminViewTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.staff_user = User.objects.create_user(
            username="book-lookup-admin",
            employee_id=700002,
            password="password123",
            is_staff=True,
        )

    def test_isbn_lookup_requires_staff_login(self):
        response = self.client.get(reverse("admin_books_isbn_lookup"), {"isbn": "9784003101018"})

        self.assertEqual(response.status_code, 302)
        self.assertIn("/admin/login/", response["Location"])

    def test_isbn_lookup_returns_existing_book_data_as_json(self):
        self.client.force_login(self.staff_user)
        genre = Genre.objects.create(c_code_genre="41", name="数学")
        Book.objects.create(
            genre=genre,
            isbn="9784003101018",
            title="既存書籍",
            author="既存著者",
            publisher="既存出版社",
            published_date=date(1990, 4, 1),
            price=1200,
            cover_image_url="https://example.com/existing.jpg",
        )

        response = self.client.get(
            reverse("admin_books_isbn_lookup"), {"isbn": "978-4-00-310101-8"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "book": {
                    "isbn": "9784003101018",
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

    def test_isbn_lookup_returns_400_for_invalid_isbn(self):
        self.client.force_login(self.staff_user)

        response = self.client.get(reverse("admin_books_isbn_lookup"), {"isbn": "4003101014"})

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"error": "ISBNは13桁で入力してください"})

    def test_isbn_lookup_returns_404_when_book_is_not_found(self):
        self.client.force_login(self.staff_user)

        with patch("books.services.openbd.fetch_openbd_book_data", return_value=None):
            response = self.client.get(
                reverse("admin_books_isbn_lookup"), {"isbn": "9784003101018"}
            )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"error": "書籍情報が見つかりませんでした"})

    def test_isbn_lookup_returns_502_when_openbd_fails(self):
        self.client.force_login(self.staff_user)

        with patch(
            "books.services.openbd.fetch_openbd_book_data", side_effect=OpenBdError("timeout")
        ):
            response = self.client.get(
                reverse("admin_books_isbn_lookup"), {"isbn": "9784003101018"}
            )

        self.assertEqual(response.status_code, 502)
        self.assertEqual(response.json(), {"error": "openBDから書籍情報を取得できませんでした"})


class BookRegisterFormTests(TestCase):
    def test_form_widgets_match_ui_design_ids_and_placeholders(self):
        form = BookRegisterForm()

        expected_attrs = {
            "isbn": {"id": "input_isbn", "placeholder": "ISBNコード"},
            "title": {"id": "input_title", "placeholder": "タイトル"},
            "author": {"id": "input_author", "placeholder": "著者"},
            "published_date": {"id": "input_publication_date", "placeholder": "出版日"},
            "publisher": {"id": "input_publisher", "placeholder": "出版社"},
            "cover_image_url": {"id": "input_image_url", "placeholder": "画像用リンク"},
            "price": {"id": "input_price", "placeholder": "価格"},
            "genre_code": {"id": "input_ccode", "placeholder": "Cコード"},
            "purchase_date": {"id": "input_purchase_date"},
            "location": {"id": "input_location", "placeholder": "保管場所"},
            "copy_count": {
                "id": "input_num_of_books",
                "placeholder": "版数",
                "inputmode": "numeric",
            },
        }

        for field_name, attrs in expected_attrs.items():
            with self.subTest(field_name=field_name):
                for attr_name, expected_value in attrs.items():
                    self.assertEqual(
                        form.fields[field_name].widget.attrs[attr_name], expected_value
                    )

        self.assertEqual(form.fields["purchase_date"].widget.input_type, "date")

    def test_valid_form_normalizes_isbn_and_cleans_typed_values(self):
        genre = Genre.objects.create(c_code_genre="55", name="電気通信")

        form = BookRegisterForm(
            data={
                "isbn": "978-4-00-310101-8",
                "title": "吾輩は猫である",
                "author": "夏目漱石",
                "publisher": "岩波書店",
                "published_date": "1990-04-01",
                "cover_image_url": "https://example.com/cover.jpg",
                "price": "1200",
                "genre_code": genre.c_code_genre,
                "purchase_date": "2026-06-07",
                "location": "1F-A-01",
                "copy_count": "3",
            }
        )

        self.assertEqual(form.is_valid(), True, form.errors)
        self.assertEqual(form.cleaned_data["isbn"], "9784003101018")
        self.assertEqual(form.cleaned_data["published_date"], date(1990, 4, 1))
        self.assertEqual(form.cleaned_data["purchase_date"], date(2026, 6, 7))
        self.assertEqual(form.cleaned_data["price"], 1200)
        self.assertEqual(form.cleaned_data["genre_code"], "55")
        self.assertEqual(form.cleaned_data["copy_count"], 3)

    def test_optional_fields_can_be_blank(self):
        form = BookRegisterForm(
            data={
                "isbn": "9784003101018",
                "title": "吾輩は猫である",
                "author": "",
                "publisher": "",
                "published_date": "",
                "cover_image_url": "",
                "price": "",
                "genre_code": "",
                "purchase_date": "",
                "location": "1F-A-01",
                "copy_count": "1",
            }
        )

        self.assertEqual(form.is_valid(), True, form.errors)
        self.assertEqual(form.cleaned_data["author"], "")
        self.assertEqual(form.cleaned_data["publisher"], "")
        self.assertEqual(form.cleaned_data["published_date"], None)
        self.assertEqual(form.cleaned_data["cover_image_url"], "")
        self.assertEqual(form.cleaned_data["price"], None)
        self.assertEqual(form.cleaned_data["genre_code"], "")
        self.assertEqual(form.cleaned_data["purchase_date"], None)

    def test_required_fields_are_invalid_when_blank(self):
        form = BookRegisterForm(data={})

        self.assertEqual(form.is_valid(), False)
        self.assertIn("isbn", form.errors)
        self.assertIn("title", form.errors)
        self.assertIn("location", form.errors)
        self.assertIn("copy_count", form.errors)

    def test_form_rejects_invalid_isbn(self):
        form = BookRegisterForm(
            data={
                "isbn": "4003101014",
                "title": "吾輩は猫である",
                "location": "1F-A-01",
                "copy_count": "1",
            }
        )

        self.assertEqual(form.is_valid(), False)
        self.assertIn("isbn", form.errors)

    def test_form_rejects_negative_price(self):
        form = BookRegisterForm(
            data={
                "isbn": "9784003101018",
                "title": "吾輩は猫である",
                "price": "-1",
                "location": "1F-A-01",
                "copy_count": "1",
            }
        )

        self.assertEqual(form.is_valid(), False)
        self.assertIn("price", form.errors)

    def test_form_rejects_price_over_max(self):
        form = BookRegisterForm(
            data={
                "isbn": "9784003101018",
                "title": "吾輩は猫である",
                "price": "10000000",
                "location": "1F-A-01",
                "copy_count": "1",
            }
        )

        self.assertEqual(form.is_valid(), False)
        self.assertIn("price", form.errors)

    def test_form_accepts_max_price(self):
        form = BookRegisterForm(
            data={
                "isbn": "9784003101018",
                "title": "吾輩は猫である",
                "price": "9999999",
                "location": "1F-A-01",
                "copy_count": "1",
            }
        )

        self.assertEqual(form.is_valid(), True, form.errors)
        self.assertEqual(form.cleaned_data["price"], 9999999)

    def test_form_rejects_unknown_genre_code(self):
        form = BookRegisterForm(
            data={
                "isbn": "9784003101018",
                "title": "吾輩は猫である",
                "genre_code": "99",
                "location": "1F-A-01",
                "copy_count": "1",
            }
        )

        self.assertEqual(form.is_valid(), False)
        self.assertIn("genre_code", form.errors)

    def test_form_rejects_non_positive_copy_count(self):
        form = BookRegisterForm(
            data={
                "isbn": "9784003101018",
                "title": "吾輩は猫である",
                "location": "1F-A-01",
                "copy_count": "0",
            }
        )

        self.assertEqual(form.is_valid(), False)
        self.assertIn("copy_count", form.errors)

    def test_form_rejects_copy_count_over_max(self):
        form = BookRegisterForm(
            data={
                "isbn": "9784003101018",
                "title": "吾輩は猫である",
                "location": "1F-A-01",
                "copy_count": "101",
            }
        )

        self.assertEqual(form.is_valid(), False)
        self.assertIn("copy_count", form.errors)

    def test_form_accepts_max_copy_count(self):
        form = BookRegisterForm(
            data={
                "isbn": "9784003101018",
                "title": "吾輩は猫である",
                "location": "1F-A-01",
                "copy_count": "100",
            }
        )

        self.assertEqual(form.is_valid(), True, form.errors)
        self.assertEqual(form.cleaned_data["copy_count"], 100)
