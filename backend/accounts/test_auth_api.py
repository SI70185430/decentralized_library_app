from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse

LOGIN_USERNAME = "ログイン確認用"
LOGIN_EMPLOYEE_ID = 7777
UNKNOWN_EMPLOYEE_ID = 999999
LOGIN_PASSWORD = "ifhWhjV3"
INVALID_LOGIN_MESSAGE = "社員番号またはパスワードが正しくありません"
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
            {"employee_id": "７７７７", "password": LOGIN_PASSWORD},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["user"]["employee_id"], LOGIN_EMPLOYEE_ID)

    def test_login_requires_employee_id(self):
        response = self.post_login({"password": LOGIN_PASSWORD})

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"employee_id": ["この項目は必須です。"]})
        self.assertNotIn("sessionid", self.client.cookies)

    def test_login_requires_password(self):
        response = self.post_login({"employee_id": LOGIN_EMPLOYEE_ID})

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"password": ["この項目は必須です。"]})
        self.assertNotIn("sessionid", self.client.cookies)

    def test_login_rejects_invalid_employee_id_type(self):
        response = self.post_login({"employee_id": "not-number", "password": LOGIN_PASSWORD})

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"employee_id": ["有効な整数を入力してください。"]})
        self.assertNotIn("sessionid", self.client.cookies)

    def test_login_rejects_wrong_password(self):
        response = self.post_login(
            {"employee_id": LOGIN_EMPLOYEE_ID, "password": "wrong-password"},
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"non_field_errors": [INVALID_LOGIN_MESSAGE]})
        self.assertNotIn("sessionid", self.client.cookies)

    def test_login_rejects_unknown_employee_id(self):
        response = self.post_login(
            {"employee_id": UNKNOWN_EMPLOYEE_ID, "password": LOGIN_PASSWORD},
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"non_field_errors": [INVALID_LOGIN_MESSAGE]})
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
