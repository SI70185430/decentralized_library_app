from datetime import date

from django.test import TestCase

from books.forms import BookRegisterForm
from books.tests.helpers import (
    INVALID_ISBN,
    VALID_ISBN,
    book_register_form_data,
    create_genre,
)


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
        genre = create_genre()

        form = BookRegisterForm(
            data=book_register_form_data(
                genre_code=genre.c_code_genre,
                copy_count="3",
            )
        )

        self.assertEqual(form.is_valid(), True, form.errors)
        self.assertEqual(form.cleaned_data["isbn"], VALID_ISBN)
        self.assertEqual(form.cleaned_data["published_date"], date(1990, 4, 1))
        self.assertEqual(form.cleaned_data["purchase_date"], date(2026, 6, 7))
        self.assertEqual(form.cleaned_data["price"], 1200)
        self.assertEqual(form.cleaned_data["genre_code"], "55")
        self.assertEqual(form.cleaned_data["copy_count"], 3)

    def test_optional_fields_can_be_blank(self):
        form = BookRegisterForm(
            data=book_register_form_data(
                isbn=VALID_ISBN,
                author="",
                publisher="",
                published_date="",
                cover_image_url="",
                price="",
                genre_code="",
                purchase_date="",
            )
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
        form = BookRegisterForm(data=book_register_form_data(isbn=INVALID_ISBN))

        self.assertEqual(form.is_valid(), False)
        self.assertIn("isbn", form.errors)

    def test_form_rejects_negative_price(self):
        form = BookRegisterForm(data=book_register_form_data(isbn=VALID_ISBN, price="-1"))

        self.assertEqual(form.is_valid(), False)
        self.assertIn("price", form.errors)

    def test_form_rejects_price_over_max(self):
        form = BookRegisterForm(data=book_register_form_data(isbn=VALID_ISBN, price="10000000"))

        self.assertEqual(form.is_valid(), False)
        self.assertIn("price", form.errors)

    def test_form_accepts_max_price(self):
        form = BookRegisterForm(data=book_register_form_data(isbn=VALID_ISBN, price="9999999"))

        self.assertEqual(form.is_valid(), True, form.errors)
        self.assertEqual(form.cleaned_data["price"], 9999999)

    def test_form_rejects_unknown_genre_code(self):
        form = BookRegisterForm(data=book_register_form_data(isbn=VALID_ISBN, genre_code="99"))

        self.assertEqual(form.is_valid(), False)
        self.assertIn("genre_code", form.errors)

    def test_form_rejects_non_positive_copy_count(self):
        form = BookRegisterForm(data=book_register_form_data(isbn=VALID_ISBN, copy_count="0"))

        self.assertEqual(form.is_valid(), False)
        self.assertIn("copy_count", form.errors)

    def test_form_rejects_copy_count_over_max(self):
        form = BookRegisterForm(data=book_register_form_data(isbn=VALID_ISBN, copy_count="101"))

        self.assertEqual(form.is_valid(), False)
        self.assertIn("copy_count", form.errors)

    def test_form_accepts_max_copy_count(self):
        form = BookRegisterForm(data=book_register_form_data(isbn=VALID_ISBN, copy_count="100"))

        self.assertEqual(form.is_valid(), True, form.errors)
        self.assertEqual(form.cleaned_data["copy_count"], 100)
