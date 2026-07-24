from datetime import date

from django.test import RequestFactory, TestCase

from books.serializers import (
    BookDetailSerializer,
    BookListSerializer,
    BookSearchQuerySerializer,
    GenreSerializer,
)
from books.services.book_search import BookSearchParams
from books.tests.helpers import (
    DEFAULT_COVER_IMAGE_URL,
    INVALID_ISBN,
    INVALID_ISBN13_CHECK_DIGIT,
    VALID_ISBN,
    VALID_ISBN10,
    VALID_ISBN_WITH_HYPHENS,
    create_book,
    create_genre,
    create_staff_user,
)


class BookSearchQuerySerializerTests(TestCase):
    def test_trims_text_fields_and_converts_to_params(self):
        serializer = BookSearchQuerySerializer(
            data={
                "keyword": "  cats  ",
                "title": "  title  ",
                "author": "  author  ",
                "publisher": "  publisher  ",
            }
        )

        self.assertEqual(serializer.is_valid(), True, serializer.errors)
        self.assertEqual(
            serializer.to_params(),
            BookSearchParams(
                keyword="cats",
                title="title",
                author="author",
                publisher="publisher",
            ),
        )

    def test_missing_fields_are_empty_strings_in_params(self):
        serializer = BookSearchQuerySerializer(data={})

        self.assertEqual(serializer.is_valid(), True, serializer.errors)
        self.assertEqual(serializer.to_params(), BookSearchParams())

    def test_blank_fields_are_empty_strings_in_params(self):
        serializer = BookSearchQuerySerializer(
            data={
                "keyword": "",
                "title": "",
                "author": "",
                "publisher": "",
                "isbn": "",
                "genre": "",
            }
        )

        self.assertEqual(serializer.is_valid(), True, serializer.errors)
        self.assertEqual(serializer.to_params(), BookSearchParams())

    def test_normalizes_hyphenated_isbn13(self):
        serializer = BookSearchQuerySerializer(data={"isbn": VALID_ISBN_WITH_HYPHENS})

        self.assertEqual(serializer.is_valid(), True, serializer.errors)
        self.assertEqual(serializer.to_params().isbn, VALID_ISBN)

    def test_normalizes_isbn10_to_isbn13(self):
        serializer = BookSearchQuerySerializer(data={"isbn": VALID_ISBN10})

        self.assertEqual(serializer.is_valid(), True, serializer.errors)
        self.assertEqual(serializer.to_params().isbn, VALID_ISBN)

    def test_invalid_isbn_adds_isbn_field_error(self):
        serializer = BookSearchQuerySerializer(data={"isbn": INVALID_ISBN})

        self.assertEqual(serializer.is_valid(), False)
        self.assertIn("isbn", serializer.errors)
        self.assertIn(
            "10桁または13桁で正当なISBNを入力してください",
            str(serializer.errors["isbn"][0]),
        )

    def test_invalid_isbn13_check_digit_adds_isbn_field_error(self):
        serializer = BookSearchQuerySerializer(data={"isbn": INVALID_ISBN13_CHECK_DIGIT})

        self.assertEqual(serializer.is_valid(), False)
        self.assertIn("isbn", serializer.errors)
        self.assertIn(
            "10桁または13桁で正当なISBNを入力してください",
            str(serializer.errors["isbn"][0]),
        )

    def test_existing_genre_is_valid(self):
        create_genre(code="55", name="電子通信")
        serializer = BookSearchQuerySerializer(data={"genre": "55"})

        self.assertEqual(serializer.is_valid(), True, serializer.errors)
        self.assertEqual(serializer.to_params().genre, "55")

    def test_unknown_genre_adds_genre_field_error(self):
        serializer = BookSearchQuerySerializer(data={"genre": "99"})

        self.assertEqual(serializer.is_valid(), False)
        self.assertIn("genre", serializer.errors)
        self.assertIn("存在するジャンルを指定してください", str(serializer.errors["genre"][0]))

    def test_category_fields_are_not_search_params(self):
        serializer = BookSearchQuerySerializer(data={"category": "5", "category_code": "5"})

        self.assertEqual(serializer.is_valid(), True, serializer.errors)
        self.assertEqual(serializer.to_params(), BookSearchParams())


class BookResponseSerializerTests(TestCase):
    def test_genre_serializer_returns_category_code_and_name(self):
        genre = create_genre(code="55", name="電子通信")

        self.assertEqual(
            GenreSerializer(genre).data,
            {
                "category_code": "5",
                "category_name": "工学・工業",
                "c_code_genre": "55",
                "name": "電子通信",
            },
        )

    def test_book_list_serializer_returns_expected_fields(self):
        genre = create_genre(code="55", name="電子通信")
        book = create_book(
            genre=genre,
            isbn=VALID_ISBN,
            title="吾輩は猫である",
            author="夏目漱石",
            publisher="岩波書店",
            published_date=date(1990, 4, 1),
            price=1200,
            cover_image_url=DEFAULT_COVER_IMAGE_URL,
            description="猫の小説",
        )

        data = BookListSerializer(book).data

        self.assertEqual(data["id"], str(book.id))
        self.assertEqual(data["isbn"], VALID_ISBN)
        self.assertEqual(data["title"], "吾輩は猫である")
        self.assertEqual(data["author"], "夏目漱石")
        self.assertEqual(data["publisher"], "岩波書店")
        self.assertEqual(data["published_date"], "1990-04-01")
        self.assertEqual(data["price"], 1200)
        self.assertEqual(data["cover_image_url"], DEFAULT_COVER_IMAGE_URL)
        self.assertEqual(data["description"], "猫の小説")
        self.assertEqual(data["genre"]["category_code"], "5")
        self.assertEqual(data["genre"]["category_name"], "工学・工業")
        self.assertEqual(data["genre"]["c_code_genre"], "55")
        self.assertEqual(data["genre"]["name"], "電子通信")

    def test_book_detail_serializer_returns_same_basic_fields(self):
        genre = create_genre(code="90", name="文学")
        book = create_book(genre=genre, isbn=VALID_ISBN, title="Detail Book")
        request = RequestFactory().get("/")
        request.user = create_staff_user()

        data = BookDetailSerializer(book, context={"request": request}).data

        self.assertEqual(data["id"], str(book.id))
        self.assertEqual(data["isbn"], VALID_ISBN)
        self.assertEqual(data["title"], "Detail Book")
        self.assertEqual(data["genre"]["category_code"], "9")
        self.assertEqual(data["genre"]["category_name"], "文学")

    def test_book_serializer_returns_null_genre_when_book_has_no_genre(self):
        book = create_book(isbn=VALID_ISBN, title="No Genre")

        self.assertIsNone(BookListSerializer(book).data["genre"])
