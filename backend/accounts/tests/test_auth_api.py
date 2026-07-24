from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from config.api_errors import ApiErrorCode

LOGIN_USERNAME = "認証API確認用"
LOGIN_EMPLOYEE_ID = 888888
UNKNOWN_EMPLOYEE_ID = 999999
LOGIN_PASSWORD = "testloginlogoutme"
FRONTEND_ORIGIN = "https://localhost:3000"


@override_settings(
    SESSION_COOKIE_SECURE=True,
    CSRF_COOKIE_SECURE=True,
    SESSION_COOKIE_SAMESITE="Strict",
    CSRF_COOKIE_SAMESITE="Strict",
)
class AuthApiTests(TestCase):
    def setUp(self):
        self.client = Client(enforce_csrf_checks=True)
        User = get_user_model()
        self.user = User.objects.create_user(
            username=LOGIN_USERNAME,
            employee_id=LOGIN_EMPLOYEE_ID,
            password=LOGIN_PASSWORD,
        )

    def get_csrf_response(self):
        return self.client.get(reverse("accounts:csrf"), secure=True)

    def get_csrf_token(self) -> str:
        csrf_response = self.get_csrf_response()
        return csrf_response.cookies["csrftoken"].value

    def get_me_response(self):
        return self.client.get(reverse("accounts:me"), secure=True)

    def post_login(self, data: dict[str, str | int]):
        return self.client.post(
            reverse("accounts:login"),
            data,
            content_type="application/json",
            HTTP_X_CSRFTOKEN=self.get_csrf_token(),
            HTTP_ORIGIN=FRONTEND_ORIGIN,
            secure=True,
        )

    def assert_validation_errors_for(self, response, *fields: str):
        self.assertEqual(response.status_code, 400)
        errors = response.json()
        self.assertEqual(errors["code"], ApiErrorCode.VALIDATION_ERROR.value)
        field_errors = errors["field_errors"]
        self.assertEqual(set(field_errors.keys()), set(fields))
        for field in fields:
            self.assertTrue(field_errors[field])
        self.assertNotIn("sessionid", self.client.cookies)

    def test_csrf_endpoint_sets_csrf_cookie(self):
        response = self.get_csrf_response()

        self.assertEqual(response.status_code, 200)
        self.assertIn("csrftoken", response.cookies)
        self.assertTrue(response.cookies["csrftoken"]["secure"])
        self.assertEqual(response.cookies["csrftoken"]["samesite"], "Strict")

    def test_login(self):
        response = self.post_login(
            {"employee_id": LOGIN_EMPLOYEE_ID, "password": LOGIN_PASSWORD},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "user": {
                    "id": str(self.user.id),
                    "employee_id": LOGIN_EMPLOYEE_ID,
                    "username": LOGIN_USERNAME,
                }
            },
        )
        self.assertIn("sessionid", self.client.cookies)
        self.assertTrue(self.client.cookies["sessionid"]["secure"])
        self.assertEqual(self.client.cookies["sessionid"]["samesite"], "Strict")

    def test_login_accepts_full_width_employee_id(self):
        response = self.post_login(
            {"employee_id": "８８８８８８", "password": LOGIN_PASSWORD},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["user"]["employee_id"], LOGIN_EMPLOYEE_ID)

    def test_login_requires_employee_id(self):
        response = self.post_login({"password": LOGIN_PASSWORD})

        self.assert_validation_errors_for(response, "employee_id")

    def test_login_requires_password(self):
        response = self.post_login({"employee_id": LOGIN_EMPLOYEE_ID})

        self.assert_validation_errors_for(response, "password")

    def test_login_requires_employee_id_and_password(self):
        response = self.post_login({})

        self.assert_validation_errors_for(response, "employee_id", "password")

    def test_login_rejects_invalid_employee_id_type(self):
        response = self.post_login({"employee_id": "not-number", "password": LOGIN_PASSWORD})

        self.assert_validation_errors_for(response, "employee_id")

    def test_login_rejects_wrong_password(self):
        response = self.post_login(
            {"employee_id": LOGIN_EMPLOYEE_ID, "password": "wrong-password"},
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json(),
            {
                "code": ApiErrorCode.VALIDATION_ERROR.value,
                "field_errors": {"non_field_errors": [ApiErrorCode.INVALID_CREDENTIALS.value]},
            },
        )
        self.assertNotIn("sessionid", self.client.cookies)

    def test_login_rejects_unknown_employee_id(self):
        response = self.post_login(
            {"employee_id": UNKNOWN_EMPLOYEE_ID, "password": LOGIN_PASSWORD},
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json(),
            {
                "code": ApiErrorCode.VALIDATION_ERROR.value,
                "field_errors": {"non_field_errors": [ApiErrorCode.INVALID_CREDENTIALS.value]},
            },
        )
        self.assertNotIn("sessionid", self.client.cookies)

    def test_me_returns_authenticated_user(self):
        self.client.force_login(self.user)

        response = self.get_me_response()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "user": {
                    "id": str(self.user.id),
                    "employee_id": LOGIN_EMPLOYEE_ID,
                    "username": LOGIN_USERNAME,
                }
            },
        )

    def test_me_rejects_anonymous_user(self):
        response = self.get_me_response()

        self.assertEqual(response.status_code, 403)

    def test_logout_removes_session(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("accounts:logout"),
            {},
            content_type="application/json",
            HTTP_X_CSRFTOKEN=self.get_csrf_token(),
            HTTP_ORIGIN=FRONTEND_ORIGIN,
            secure=True,
        )

        self.assertEqual(response.status_code, 200)
        response = self.get_me_response()
        self.assertEqual(response.status_code, 403)
