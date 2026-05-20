import uuid

from datetime import date, datetime

from django.db import IntegrityError
from django.test import TestCase

from accounts.models import AppUser


class AppUserModelTests(TestCase):
    def setUp(self):
        self.instance = AppUser.objects.create_user(
            username="1001",
            employee_id=1001,
            password="password123",
            is_staff=False,
            is_active=True,
        )

    def test_field_attributes(self):
        field = AppUser._meta.get_field("id")
        self.assertEqual(field.primary_key, True)
        self.assertEqual(field.editable, False)
        self.assertEqual(field.default, uuid.uuid7)
        self.assertEqual(field.verbose_name, "ユーザーID")

        field = AppUser._meta.get_field("username")
        self.assertEqual(field.max_length, 150)
        self.assertEqual(field.unique, True)

        field = AppUser._meta.get_field("employee_id")
        self.assertEqual(field.unique, True)
        self.assertEqual(field.verbose_name, "社員番号")

        field = AppUser._meta.get_field("password")
        self.assertEqual(field.max_length, 128)

        field = AppUser._meta.get_field("is_staff")
        self.assertEqual(field.default, False)

        field = AppUser._meta.get_field("is_active")
        self.assertEqual(field.default, True)

        field = AppUser._meta.get_field("last_login")
        self.assertEqual(field.null, True)
        self.assertEqual(field.blank, True)

        self.assertEqual(AppUser.REQUIRED_FIELDS, ["employee_id"])

    def test_db_table(self):
        self.assertEqual(AppUser._meta.db_table, "app_user")

    def test_create_data(self):
        user = AppUser.objects.create_user(
            username="created_user",
            employee_id=1002,
            password="password123",
        )
        self.assertIsNotNone(user.id)

    def test_retrieve_data(self):
        user = AppUser.objects.get(id=self.instance.id)

        self.assertEqual(user.username, "1001")
        self.assertEqual(user.employee_id, 1001)
        self.assertFalse(user.is_staff)
        self.assertTrue(user.is_active)
        self.assertTrue(user.check_password("password123"))  # ハッシュ化した値を検証

    def test_retrieve_nonexistent_data(self):
        with self.assertRaises(AppUser.DoesNotExist):
            AppUser.objects.get(employee_id=999999)

    def test_delete_data(self):
        self.instance.delete()
        with self.assertRaises(AppUser.DoesNotExist):
            AppUser.objects.get(id=self.instance.id)

    def test_update_data(self):
        self.instance.username = "updated_user"
        self.instance.save()
        updated_user = AppUser.objects.get(id=self.instance.id)
        self.assertEqual(updated_user.username, "updated_user")

    def test_check_constraint(self):
        with self.assertRaises(IntegrityError):
            AppUser.objects.create_user(
                username="invalid_employee",
                employee_id=0,
                password="password123",
            )

    def test_auto_timestamp_fields_and_last_login(self):
        user = AppUser.objects.create_user(
            username="timestamp_test_user",
            employee_id=1005,
            password="password123",
        )
        self.assertIsInstance(user.date_joined, datetime)
        self.assertIsInstance(user.updated_at, datetime)
        self.assertIsNone(user.last_login)
