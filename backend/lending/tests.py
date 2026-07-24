import uuid
from datetime import date, datetime

from django.db import IntegrityError, models, transaction
from django.test import TestCase

from accounts.models import AppUser
from books.models import Book, BookCopy, Genre
from lending.models import Lending, Reservation


class LendingModelTests(TestCase):
    def setUp(self):
        self.user = AppUser.objects.create_user(
            username="lending_user",
            employee_id=3001,
            password="password123",
        )
        self.genre = Genre.objects.get(c_code_genre="10")
        self.book = Book.objects.create(
            genre=self.genre,
            isbn="9784222222222",
            title="lending test book",
        )
        self.book_copy = BookCopy.objects.create(
            book=self.book,
            location="1F-L-01",
        )
        self.instance = Lending.objects.create(
            book_copy=self.book_copy,
            user=self.user,
            borrowed_date=date(2026, 5, 1),
            due_date=date(2026, 6, 9),
            returned_date=date(2026, 5, 10),
            extension_count=1,
        )

    # 複合ユニーク制約回避のための蔵書作成ヘルパー
    def create_book_copy(self, location):
        return BookCopy.objects.create(
            book=self.book,
            location=location,
        )

    def test_field_attributes(self):
        field = Lending._meta.get_field("id")
        self.assertEqual(field.primary_key, True)
        self.assertEqual(field.editable, False)
        self.assertEqual(field.default, uuid.uuid7)
        self.assertEqual(field.verbose_name, "貸出ID")

        field = Lending._meta.get_field("book_copy")
        self.assertEqual(field.verbose_name, "蔵書ID")
        self.assertEqual(field.remote_field.model, BookCopy)
        self.assertEqual(field.remote_field.on_delete, models.RESTRICT)
        self.assertEqual(field.remote_field.related_name, "lending")
        self.assertEqual(field.column, "book_copy_id")

        field = Lending._meta.get_field("user")
        self.assertEqual(field.verbose_name, "ユーザID")
        self.assertEqual(field.remote_field.model, AppUser)
        self.assertEqual(field.remote_field.on_delete, models.RESTRICT)
        self.assertEqual(field.remote_field.related_name, "lending")
        self.assertEqual(field.column, "user_id")

        field = Lending._meta.get_field("borrowed_date")
        self.assertEqual(field.verbose_name, "貸出日")

        field = Lending._meta.get_field("due_date")
        self.assertEqual(field.verbose_name, "返却期限日")

        field = Lending._meta.get_field("returned_date")
        self.assertEqual(field.null, True)
        self.assertEqual(field.blank, True)
        self.assertEqual(field.verbose_name, "実返却日")

        field = Lending._meta.get_field("extension_count")
        self.assertEqual(field.default, 0)
        self.assertEqual(field.verbose_name, "延長回数")

    def test_db_table(self):
        self.assertEqual(Lending._meta.db_table, "lending")

    def test_create_data(self):
        book_copy = self.create_book_copy("2F-M-02")
        lending = Lending.objects.create(
            book_copy=book_copy,
            user=self.user,
            borrowed_date=date(2026, 6, 1),
            due_date=date(2026, 6, 30),
        )
        self.assertIsNotNone(lending.id)

    def test_retrieve_data(self):
        lending = Lending.objects.get(id=self.instance.id)

        self.assertEqual(lending.book_copy_id, self.book_copy.id)
        self.assertEqual(lending.user_id, self.user.id)
        self.assertEqual(lending.borrowed_date, date(2026, 5, 1))
        self.assertEqual(lending.due_date, date(2026, 6, 9))
        self.assertEqual(lending.returned_date, date(2026, 5, 10))
        self.assertEqual(lending.extension_count, 1)
        self.assertEqual(
            lending.book_copy.location, "1F-L-01"
        )  # 貸出処理完了時の保管場所の呼び出しを想定

    def test_retrieve_nonexistent_data(self):
        book_copy = self.create_book_copy("3F-N-03")
        with self.assertRaises(Lending.DoesNotExist):
            Lending.objects.get(book_copy=book_copy)

    def test_delete_data(self):
        self.instance.delete()
        with self.assertRaises(Lending.DoesNotExist):
            Lending.objects.get(id=self.instance.id)

    def test_update_data(self):
        self.instance.returned_date = date(2026, 6, 19)
        self.instance.extension_count = 2
        self.instance.save()
        updated_lending = Lending.objects.get(id=self.instance.id)
        self.assertEqual(updated_lending.returned_date, date(2026, 6, 19))
        self.assertEqual(updated_lending.extension_count, 2)

    def test_check_constraint(self):
        invalid_lendings = [
            (
                "due_date_before_borrowed_date",
                {
                    "book_copy": self.create_book_copy("3F-L-03"),
                    "borrowed_date": date(2026, 7, 10),
                    "due_date": date(2026, 7, 9),
                },
            ),
            (
                "returned_date_before_borrowed_date",
                {
                    "book_copy": self.create_book_copy("3F-L-04"),
                    "borrowed_date": date(2026, 7, 10),
                    "due_date": date(2026, 7, 20),
                    "returned_date": date(2026, 7, 9),
                },
            ),
            (
                "extension_count_too_small",
                {
                    "book_copy": self.create_book_copy("3F-L-05"),
                    "borrowed_date": date(2026, 7, 10),
                    "due_date": date(2026, 7, 20),
                    "extension_count": -1,
                },
            ),
            (
                "extension_count_too_large",
                {
                    "book_copy": self.create_book_copy("3F-L-06"),
                    "borrowed_date": date(2026, 7, 10),
                    "due_date": date(2026, 7, 20),
                    "extension_count": 4,
                },
            ),
        ]

        for name, data in invalid_lendings:
            with (
                self.subTest(name=name),
                self.assertRaises(IntegrityError),
                transaction.atomic(),
            ):
                Lending.objects.create(user=self.user, **data)

    def test_returned_lending_history_allows_same_book_copy_and_user(self):
        lending = Lending.objects.create(
            book_copy=self.book_copy,
            user=self.user,
            borrowed_date=date(2026, 7, 1),
            due_date=date(2026, 7, 30),
            extension_count=0,
        )

        self.assertIsNotNone(lending.id)

    def test_unique_constraint_active_lending_per_book_copy(self):
        active_lending = Lending.objects.create(
            book_copy=self.create_book_copy("active lending copy"),
            user=self.user,
            borrowed_date=date(2026, 7, 1),
            due_date=date(2026, 7, 30),
            extension_count=0,
        )
        another_user = AppUser.objects.create_user(
            username="another_lending_user",
            employee_id=3002,
            password="password123",
        )

        with self.assertRaises(IntegrityError), transaction.atomic():
            Lending.objects.create(
                book_copy=active_lending.book_copy,
                user=another_user,
                borrowed_date=date(2026, 7, 2),
                due_date=date(2026, 7, 31),
                extension_count=0,
            )

    def test_auto_timestamp_fields(self):
        book_copy = self.create_book_copy("timestamp test")
        lending = Lending.objects.create(
            book_copy=book_copy,
            user=self.user,
            borrowed_date=date(2026, 6, 1),
            due_date=date(2026, 6, 30),
        )
        self.assertIsInstance(lending.created_at, datetime)
        self.assertIsInstance(lending.updated_at, datetime)


class ReservationModelTests(TestCase):
    def setUp(self):
        self.user = AppUser.objects.create_user(
            username="reservation_user",
            employee_id=3001,
            password="password123",
        )
        self.genre = Genre.objects.get(c_code_genre="82")
        self.book = Book.objects.create(
            genre=self.genre,
            isbn="9784333333333",
            title="reservation test book",
        )
        self.book_copy = BookCopy.objects.create(
            book=self.book,
            location="1F-R-01",
        )
        self.instance = Reservation.objects.create(
            book_copy=self.book_copy,
            user=self.user,
            scheduled_date=date(2026, 5, 20),
            expires_date=date(2026, 5, 29),
        )

    # 複合ユニーク制約回避のための蔵書作成ヘルパー
    def create_book_copy(self, location):
        return BookCopy.objects.create(
            book=self.book,
            location=location,
        )

    def test_field_attributes(self):
        field = Reservation._meta.get_field("id")
        self.assertEqual(field.primary_key, True)
        self.assertEqual(field.editable, False)
        self.assertEqual(field.default, uuid.uuid7)
        self.assertEqual(field.verbose_name, "予約ID")

        field = Reservation._meta.get_field("book_copy")
        self.assertEqual(field.verbose_name, "蔵書ID")
        self.assertEqual(field.remote_field.model, BookCopy)
        self.assertEqual(field.remote_field.on_delete, models.CASCADE)
        self.assertEqual(field.remote_field.related_name, "reservations")
        self.assertEqual(field.column, "book_copy_id")

        field = Reservation._meta.get_field("user")
        self.assertEqual(field.verbose_name, "ユーザID")
        self.assertEqual(field.remote_field.model, AppUser)
        self.assertEqual(field.remote_field.on_delete, models.CASCADE)
        self.assertEqual(field.remote_field.related_name, "reservations")
        self.assertEqual(field.column, "user_id")

        field = Reservation._meta.get_field("scheduled_date")
        self.assertEqual(field.verbose_name, "予定貸出日")

        field = Reservation._meta.get_field("expires_date")
        self.assertEqual(field.verbose_name, "取り置き期限")

    def test_db_table(self):
        self.assertEqual(Reservation._meta.db_table, "reservation")

    def test_create_data(self):
        book_copy = self.create_book_copy("2F-R-02")
        reservation = Reservation.objects.create(
            book_copy=book_copy,
            user=self.user,
            scheduled_date=date(2026, 6, 1),
            expires_date=date(2026, 6, 10),
        )
        self.assertIsNotNone(reservation.id)

    def test_retrieve_data(self):
        reservation = Reservation.objects.get(id=self.instance.id)

        self.assertEqual(reservation.book_copy_id, self.book_copy.id)
        self.assertEqual(reservation.user_id, self.user.id)
        self.assertEqual(reservation.scheduled_date, date(2026, 5, 20))
        self.assertEqual(reservation.expires_date, date(2026, 5, 29))

    def test_retrieve_nonexistent_data(self):
        book_copy = self.create_book_copy("3F-N-03")
        with self.assertRaises(Reservation.DoesNotExist):
            Reservation.objects.get(book_copy=book_copy)

    def test_delete_data(self):
        self.instance.delete()
        with self.assertRaises(Reservation.DoesNotExist):
            Reservation.objects.get(id=self.instance.id)

    def test_update_data(self):
        self.instance.scheduled_date = date(2026, 7, 1)
        self.instance.expires_date = date(2026, 7, 30)
        self.instance.save()
        updated_reservation = Reservation.objects.get(id=self.instance.id)
        self.assertEqual(updated_reservation.scheduled_date, date(2026, 7, 1))
        self.assertEqual(updated_reservation.expires_date, date(2026, 7, 30))

    def test_check_constraint(self):
        with self.assertRaises(IntegrityError):
            Reservation.objects.create(
                book_copy=self.create_book_copy("3F-R-03"),
                user=self.user,
                scheduled_date=date(2026, 7, 10),
                expires_date=date(2026, 7, 9),
            )

    def test_unique_constraint_book_copy_user(self):
        with self.assertRaises(IntegrityError):
            Reservation.objects.create(
                book_copy=self.book_copy,
                user=self.user,
                scheduled_date=date(2026, 8, 1),
                expires_date=date(2026, 8, 10),
            )

    def test_auto_timestamp_fields(self):
        book_copy = self.create_book_copy("timestamp test")
        reservation = Reservation.objects.create(
            book_copy=book_copy,
            user=self.user,
            scheduled_date=date(2026, 6, 1),
            expires_date=date(2026, 6, 10),
        )
        self.assertIsInstance(reservation.created_at, datetime)
        self.assertIsInstance(reservation.updated_at, datetime)
