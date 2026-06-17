from django.test import TestCase
from django.urls import reverse

from books.models import Genre
from books.tests.helpers import create_genre


class GenreApiTests(TestCase):
    def setUp(self):
        Genre.objects.all().delete()

    def get_genre_list(self):
        return self.client.get(reverse("books:genre-list"))

    def test_genre_list_returns_empty_list_when_no_genres_exist(self):
        response = self.get_genre_list()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

    def test_genre_list_returns_genres(self):
        create_genre(code="55", name="電子通信")

        response = self.get_genre_list()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            [
                {
                    "category_code": "5",
                    "category_name": "工学・工業",
                    "c_code_genre": "55",
                    "name": "電子通信",
                }
            ],
        )

    def test_genre_list_orders_by_c_code_genre(self):
        create_genre(code="90", name="文学")
        create_genre(code="00", name="総記")
        create_genre(code="55", name="電子通信")

        response = self.get_genre_list()

        self.assertEqual(
            [genre["c_code_genre"] for genre in response.json()],
            ["00", "55", "90"],
        )

    def test_genre_list_returns_category_code_from_first_digit(self):
        create_genre(code="55", name="電子通信")
        create_genre(code="90", name="文学")

        response = self.get_genre_list()

        self.assertEqual(
            [(genre["c_code_genre"], genre["category_code"]) for genre in response.json()],
            [("55", "5"), ("90", "9")],
        )

    def test_genre_list_returns_category_name_from_constant_map(self):
        create_genre(code="55", name="電子通信")
        create_genre(code="90", name="文学ジャンル名")

        response = self.get_genre_list()

        self.assertEqual(
            [
                (genre["c_code_genre"], genre["category_name"], genre["name"])
                for genre in response.json()
            ],
            [
                ("55", "工学・工業", "電子通信"),
                ("90", "文学", "文学ジャンル名"),
            ],
        )

    def test_genre_list_is_not_paginated(self):
        create_genre(code="00", name="総記")

        response = self.get_genre_list()
        data = response.json()

        self.assertIsInstance(data, list)
        self.assertNotIsInstance(data, dict)

    def test_genres_url_resolves_to_genre_list_not_book_detail(self):
        create_genre(code="00", name="総記")

        response = self.client.get("/api/books/genres/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()[0]["c_code_genre"], "00")

    def test_genre_list_returns_empty_category_name_for_unknown_category_code(self):
        create_genre(code="A1", name="独自分類")

        response = self.get_genre_list()

        self.assertEqual(response.json()[0]["category_code"], "A")
        self.assertEqual(response.json()[0]["category_name"], "")
