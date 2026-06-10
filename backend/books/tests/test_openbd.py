import urllib.error
from datetime import date
from unittest.mock import patch

from django.core.exceptions import ValidationError
from django.test import TestCase

from books.services.openbd import (
    OpenBdError,
    book_to_lookup_data,
    fetch_openbd_book_data,
    lookup_book_info_by_isbn,
    map_openbd_book_data,
    normalize_isbn13,
    parse_openbd_pubdate,
)
from books.tests.helpers import (
    DEFAULT_AUTHOR,
    DEFAULT_COVER_IMAGE_URL,
    DEFAULT_PUBLISHED_DATE,
    DEFAULT_PUBLISHER,
    DEFAULT_TITLE,
    INVALID_ISBN,
    VALID_ISBN,
    VALID_ISBN_WITH_HYPHENS,
    create_book,
    create_genre,
    make_urlopen_json_response,
    openbd_book_payload,
)


class IsbnHelperTests(TestCase):
    def test_normalize_isbn13_removes_hyphens_and_spaces(self):
        self.assertEqual(normalize_isbn13(f" {VALID_ISBN_WITH_HYPHENS} "), VALID_ISBN)

    def test_normalize_isbn13_rejects_non_13_digits(self):
        invalid_values = ["", "978400310101", "97840031010180", "978400310101X", INVALID_ISBN]

        for value in invalid_values:
            with self.subTest(value=value), self.assertRaises(ValidationError):
                normalize_isbn13(value)


class OpenBdPubdateHelperTests(TestCase):
    def test_parse_openbd_pubdate_with_year(self):
        self.assertEqual(parse_openbd_pubdate("1990"), date(1990, 1, 1))

    def test_parse_openbd_pubdate_with_year_month(self):
        self.assertEqual(parse_openbd_pubdate("199004"), DEFAULT_PUBLISHED_DATE)

    def test_parse_openbd_pubdate_with_year_month_day(self):
        self.assertEqual(parse_openbd_pubdate("19900410"), date(1990, 4, 10))

    def test_parse_openbd_pubdate_returns_none_for_invalid_value(self):
        invalid_values = [None, "", "1990-04", "unknown", "199013", "19900230"]

        for value in invalid_values:
            with self.subTest(value=value):
                self.assertIsNone(parse_openbd_pubdate(value))


class OpenBdClientTests(TestCase):
    def test_fetch_openbd_book_data_returns_full_openbd_data(self):
        openbd_data = openbd_book_payload(
            summary={"isbn": VALID_ISBN, "title": DEFAULT_TITLE},
            onix={"ProductSupply": {"SupplyDetail": {"Price": {"PriceAmount": "1200"}}}},
        )
        response = make_urlopen_json_response([openbd_data])

        with patch("books.services.openbd.urllib.request.urlopen", return_value=response):
            result = fetch_openbd_book_data(VALID_ISBN)

        self.assertEqual(result, openbd_data)

    def test_fetch_openbd_book_data_returns_none_when_summary_is_not_dict(self):
        response = make_urlopen_json_response([{"summary": "invalid"}])

        with patch("books.services.openbd.urllib.request.urlopen", return_value=response):
            result = fetch_openbd_book_data(VALID_ISBN)

        self.assertIsNone(result)

    def test_fetch_openbd_book_data_returns_none_when_summary_is_empty(self):
        response = make_urlopen_json_response([{"summary": {}}])

        with patch("books.services.openbd.urllib.request.urlopen", return_value=response):
            result = fetch_openbd_book_data(VALID_ISBN)

        self.assertIsNone(result)

    def test_fetch_openbd_book_data_raises_openbd_error_on_network_error(self):
        with (
            patch(
                "books.services.openbd.urllib.request.urlopen",
                side_effect=urllib.error.URLError("timeout"),
            ),
            self.assertRaises(OpenBdError),
        ):
            fetch_openbd_book_data(VALID_ISBN)


class OpenBdMappingTests(TestCase):
    def test_map_openbd_book_data_maps_fields_from_summary_and_onix(self):
        result = map_openbd_book_data(openbd_book_payload(), VALID_ISBN)

        self.assertEqual(
            result,
            {
                "isbn": VALID_ISBN,
                "title": DEFAULT_TITLE,
                "author": DEFAULT_AUTHOR,
                "publisher": DEFAULT_PUBLISHER,
                "published_date": DEFAULT_PUBLISHED_DATE,
                "cover_image_url": DEFAULT_COVER_IMAGE_URL,
                "price": 1200,
                "genre_code": "",
            },
        )

    def test_book_to_lookup_data_maps_existing_book(self):
        genre = create_genre(code="41", name="数学")
        book = create_book(
            genre=genre,
            title="既存書籍",
            author="既存著者",
            publisher="既存出版社",
            published_date=DEFAULT_PUBLISHED_DATE,
            price=1200,
            cover_image_url="https://example.com/existing.jpg",
        )

        self.assertEqual(
            book_to_lookup_data(book),
            {
                "isbn": VALID_ISBN,
                "title": "既存書籍",
                "author": "既存著者",
                "publisher": "既存出版社",
                "published_date": DEFAULT_PUBLISHED_DATE,
                "cover_image_url": "https://example.com/existing.jpg",
                "price": 1200,
                "genre_code": "41",
            },
        )


class BookInfoLookupTests(TestCase):
    def test_lookup_book_info_by_isbn_returns_existing_book_without_openbd_call(self):
        create_book(title="既存書籍", author="既存著者")

        with patch("books.services.openbd.fetch_openbd_book_data") as fetch_openbd_book_data_mock:
            result = lookup_book_info_by_isbn(VALID_ISBN_WITH_HYPHENS)

        fetch_openbd_book_data_mock.assert_not_called()
        self.assertEqual(result["isbn"], VALID_ISBN)
        self.assertEqual(result["title"], "既存書籍")
        self.assertEqual(result["author"], "既存著者")

    def test_lookup_book_info_by_isbn_fetches_openbd_when_book_does_not_exist(self):
        with patch(
            "books.services.openbd.fetch_openbd_book_data",
            return_value=openbd_book_payload(pubdate="19900410"),
        ) as fetch_openbd_book_data_mock:
            result = lookup_book_info_by_isbn(VALID_ISBN_WITH_HYPHENS)

        fetch_openbd_book_data_mock.assert_called_once_with(VALID_ISBN)
        self.assertEqual(result["isbn"], VALID_ISBN)
        self.assertEqual(result["title"], DEFAULT_TITLE)
        self.assertEqual(result["published_date"], date(1990, 4, 10))

    def test_lookup_book_info_by_isbn_returns_none_when_openbd_has_no_data(self):
        with patch("books.services.openbd.fetch_openbd_book_data", return_value=None):
            result = lookup_book_info_by_isbn(VALID_ISBN_WITH_HYPHENS)

        self.assertIsNone(result)
