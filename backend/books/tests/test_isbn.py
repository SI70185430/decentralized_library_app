from django.core.exceptions import ValidationError
from django.test import SimpleTestCase

from books.services.isbn import normalize_isbn
from books.tests.helpers import (
    INVALID_ISBN,
    INVALID_ISBN10_CHECK_DIGIT,
    INVALID_ISBN13_CHECK_DIGIT,
    VALID_ISBN,
    VALID_ISBN10,
    VALID_ISBN10_WITH_HYPHENS,
    VALID_ISBN10_WITH_X,
    VALID_ISBN13_FROM_X_ISBN10,
    VALID_ISBN_WITH_HYPHENS,
)


class IsbnHelperTests(SimpleTestCase):
    def test_normalize_isbn_removes_hyphens_and_spaces_from_isbn13(self):
        self.assertEqual(normalize_isbn(f" {VALID_ISBN_WITH_HYPHENS} "), VALID_ISBN)

    def test_normalize_isbn_converts_isbn10_to_isbn13(self):
        self.assertEqual(normalize_isbn(VALID_ISBN10), VALID_ISBN)
        self.assertEqual(normalize_isbn(VALID_ISBN10_WITH_HYPHENS), VALID_ISBN)

    def test_normalize_isbn_converts_isbn10_with_x_to_isbn13(self):
        self.assertEqual(normalize_isbn(VALID_ISBN10_WITH_X), VALID_ISBN13_FROM_X_ISBN10)
        self.assertEqual(normalize_isbn(VALID_ISBN10_WITH_X.lower()), VALID_ISBN13_FROM_X_ISBN10)

    def test_normalize_isbn_rejects_invalid_values(self):
        invalid_values = [
            "",
            "978400310101",
            "97840031010180",
            "978400310101X",
            INVALID_ISBN,
            "abcdefghij",
            "123456789Z",
            INVALID_ISBN10_CHECK_DIGIT,
            INVALID_ISBN13_CHECK_DIGIT,
        ]

        for value in invalid_values:
            with self.subTest(value=value), self.assertRaises(ValidationError):
                normalize_isbn(value)
