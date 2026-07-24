import uuid
from datetime import date, datetime

from django.db import IntegrityError, models
from django.test import TestCase

from books.models import Book, BookCopy, Genre
from books.tests.helpers import create_book, create_book_copy, create_genre


class GenreModelTests(TestCase):
    def setUp(self):
        self.instance = create_genre(code="00", name="総記")

    def test_field_attributes(self):
        field = Genre._meta.get_field("c_code_genre")
        self.assertEqual(field.primary_key, True)
        self.assertEqual(field.max_length, 2)
        self.assertEqual(field.verbose_name, "Cコード内容")

        field = Genre._meta.get_field("name")
        self.assertEqual(field.max_length, 255)
        self.assertEqual(field.unique, True)
        self.assertEqual(field.verbose_name, "ジャンル名")

    def test_db_table(self):
        self.assertEqual(Genre._meta.db_table, "genre")

    def test_create_data(self):
        genre = create_genre(code="03", name="test")
        self.assertIsNotNone(genre.c_code_genre)

    def test_retrieve_data(self):
        genre = Genre.objects.get(c_code_genre=self.instance.c_code_genre)
        self.assertEqual(genre.name, "総記")

    def test_retrieve_nonexistent_data(self):
        with self.assertRaises(Genre.DoesNotExist):
            Genre.objects.get(c_code_genre="99")

    def test_delete_data(self):
        self.instance.delete()
        with self.assertRaises(Genre.DoesNotExist):
            Genre.objects.get(c_code_genre=self.instance.c_code_genre)

    def test_update_data(self):
        self.instance.name = "updated name"
        self.instance.save()
        updated_genre = Genre.objects.get(c_code_genre=self.instance.c_code_genre)
        self.assertEqual(updated_genre.name, "updated name")


class BookModelTests(TestCase):
    def setUp(self):
        self.genre = create_genre(code="55", name="電子通信")

        self.instance = create_book(
            genre=self.genre,
            isbn="9784285922871",
            title="foo",
            author="bar",
            publisher="baz",
            published_date=date(2026, 5, 15),
            price=5000,
            cover_image_url="https://example.com/cover.jpg",
            description="This is test book.",
        )

    def test_field_attributes(self):
        field = Book._meta.get_field("id")
        self.assertEqual(field.primary_key, True)
        self.assertEqual(field.editable, False)
        self.assertEqual(field.default, uuid.uuid7)
        self.assertEqual(field.verbose_name, "書籍ID")

        field = Book._meta.get_field("genre")
        self.assertEqual(field.verbose_name, "Cコード内容")
        self.assertEqual(field.remote_field.model, Genre)
        self.assertEqual(field.remote_field.on_delete, models.SET_NULL)
        self.assertEqual(field.remote_field.field_name, "c_code_genre")
        self.assertEqual(field.db_column, "c_code_genre")
        self.assertEqual(field.null, True)
        self.assertEqual(field.blank, True)

        field = Book._meta.get_field("isbn")
        self.assertEqual(field.max_length, 20)
        self.assertEqual(field.unique, True)
        self.assertEqual(field.verbose_name, "ISBNコード")

        field = Book._meta.get_field("title")
        self.assertEqual(field.max_length, 255)
        self.assertEqual(field.verbose_name, "タイトル")

        field = Book._meta.get_field("author")
        self.assertEqual(field.max_length, 255)
        self.assertEqual(field.null, True)
        self.assertEqual(field.blank, True)
        self.assertEqual(field.verbose_name, "著者")

        field = Book._meta.get_field("publisher")
        self.assertEqual(field.max_length, 255)
        self.assertEqual(field.null, True)
        self.assertEqual(field.blank, True)
        self.assertEqual(field.verbose_name, "出版社名")

        field = Book._meta.get_field("published_date")
        self.assertEqual(field.null, True)
        self.assertEqual(field.blank, True)
        self.assertEqual(field.verbose_name, "出版日")

        field = Book._meta.get_field("price")
        self.assertEqual(field.null, True)
        self.assertEqual(field.blank, True)
        self.assertEqual(field.verbose_name, "価格")

        field = Book._meta.get_field("cover_image_url")
        self.assertEqual(field.max_length, 500)
        self.assertEqual(field.null, True)
        self.assertEqual(field.blank, True)
        self.assertEqual(field.verbose_name, "表紙URL")

        field = Book._meta.get_field("description")
        self.assertEqual(field.null, True)
        self.assertEqual(field.blank, True)
        self.assertEqual(field.verbose_name, "説明")

    def test_db_table(self):
        self.assertEqual(Book._meta.db_table, "book")

    def test_create_data(self):
        book = Book.objects.create(
            genre=self.genre,
            isbn="9784000000000",
            title="test title",
        )
        self.assertIsNotNone(book.id)

    def test_retrieve_data(self):
        book = Book.objects.get(id=self.instance.id)

        self.assertEqual(book.genre_id, "55")
        self.assertEqual(book.genre.name, "電子通信")
        self.assertEqual(book.isbn, "9784285922871")
        self.assertEqual(book.title, "foo")
        self.assertEqual(book.author, "bar")
        self.assertEqual(book.publisher, "baz")
        self.assertEqual(book.published_date, date(2026, 5, 15))
        self.assertEqual(book.price, 5000)
        self.assertEqual(book.cover_image_url, "https://example.com/cover.jpg")
        self.assertEqual(book.description, "This is test book.")

    def test_retrieve_nonexistent_data(self):
        with self.assertRaises(Book.DoesNotExist):
            Book.objects.get(isbn="0000000000000")

    def test_delete_data(self):
        self.instance.delete()
        with self.assertRaises(Book.DoesNotExist):
            Book.objects.get(id=self.instance.id)

    def test_update_data(self):
        self.instance.title = "updated title"
        self.instance.save()
        updated_book = Book.objects.get(id=self.instance.id)
        self.assertEqual(updated_book.title, "updated title")

    def test_check_constraint(self):
        with self.assertRaises(IntegrityError):
            Book.objects.create(
                genre=self.genre,
                isbn="9784000000001",
                title="invalid price book",
                price=-1,
            )

    def test_auto_timestamp_fields(self):
        book = Book.objects.create(
            genre=self.genre,
            isbn="9784000000005",
            title="timestamp test",
        )
        self.assertIsInstance(book.created_at, datetime)
        self.assertIsInstance(book.updated_at, datetime)


class BookCopyModelTests(TestCase):
    def setUp(self):
        self.genre = create_genre(code="41", name="数学")
        self.book = create_book(
            genre=self.genre,
            isbn="9784111111111",
            title="book copy test book",
        )
        self.instance = create_book_copy(
            book=self.book,
            status=BookCopy.Status.AVAILABLE,
            location="1F-A-01",
            purchase_date=date(2026, 5, 15),
            note="This is test book copy.",
        )

    def test_field_attributes(self):
        field = BookCopy._meta.get_field("id")
        self.assertEqual(field.primary_key, True)
        self.assertEqual(field.editable, False)
        self.assertEqual(field.default, uuid.uuid7)
        self.assertEqual(field.verbose_name, "蔵書ID")

        field = BookCopy._meta.get_field("book")
        self.assertEqual(field.verbose_name, "書籍ID")
        self.assertEqual(field.remote_field.model, Book)
        self.assertEqual(field.remote_field.on_delete, models.CASCADE)
        self.assertEqual(field.remote_field.related_name, "Bookcopies")
        self.assertEqual(field.column, "book_id")

        field = BookCopy._meta.get_field("status")
        self.assertEqual(field.max_length, 20)
        self.assertEqual(field.choices, BookCopy.Status.choices)
        self.assertEqual(field.default, BookCopy.Status.AVAILABLE)
        self.assertEqual(field.verbose_name, "ステータス")

        field = BookCopy._meta.get_field("location")
        self.assertEqual(field.max_length, 255)
        self.assertEqual(field.verbose_name, "保管場所")

        field = BookCopy._meta.get_field("purchase_date")
        self.assertEqual(field.null, True)
        self.assertEqual(field.blank, True)
        self.assertEqual(field.verbose_name, "購入日")

        field = BookCopy._meta.get_field("note")
        self.assertEqual(field.null, True)
        self.assertEqual(field.blank, True)
        self.assertEqual(field.verbose_name, "備考")

    def test_db_table(self):
        self.assertEqual(BookCopy._meta.db_table, "book_copy")

    def test_create_data(self):
        book_copy = create_book_copy(
            book=self.book,
            location="2F-B-02",
        )
        self.assertIsNotNone(book_copy.id)

    def test_retrieve_data(self):
        book_copy = BookCopy.objects.get(id=self.instance.id)

        self.assertEqual(book_copy.book_id, self.book.id)
        self.assertEqual(book_copy.book.title, "book copy test book")
        self.assertEqual(book_copy.status, BookCopy.Status.AVAILABLE)
        self.assertEqual(book_copy.location, "1F-A-01")
        self.assertEqual(book_copy.purchase_date, date(2026, 5, 15))
        self.assertEqual(book_copy.note, "This is test book copy.")

    def test_retrieve_nonexistent_data(self):
        with self.assertRaises(BookCopy.DoesNotExist):
            BookCopy.objects.get(book__title="nonexistent book")

    def test_delete_data(self):
        self.instance.delete()
        with self.assertRaises(BookCopy.DoesNotExist):
            BookCopy.objects.get(id=self.instance.id)

    def test_update_data(self):
        self.instance.status = BookCopy.Status.LOST
        self.instance.location = "3F-C-03"
        self.instance.save()
        updated_book_copy = BookCopy.objects.get(id=self.instance.id)
        self.assertEqual(updated_book_copy.status, BookCopy.Status.LOST)
        self.assertEqual(updated_book_copy.location, "3F-C-03")

    def test_check_constraint(self):
        with self.assertRaises(IntegrityError):
            BookCopy.objects.create(
                book=self.book,
                status="archived",
                location="invalid status",
            )

    def test_auto_timestamp_fields(self):
        book_copy = create_book_copy(
            book=self.book,
            location="timestamp test",
        )
        self.assertIsInstance(book_copy.created_at, datetime)
        self.assertIsInstance(book_copy.updated_at, datetime)
