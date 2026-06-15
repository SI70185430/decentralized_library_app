from datetime import date
from uuid import uuid4

from django.test import TestCase
from django.urls import reverse

from books.tests.helpers import (
    DEFAULT_COVER_IMAGE_URL,
    INVALID_ISBN,
    VALID_ISBN,
    VALID_ISBN_WITH_HYPHENS,
    create_book,
    create_genre,
)


class BookSearchApiTests(TestCase):
    def setUp(self):
        self.tech_genre = create_genre(code="55", name="電気通信")
        self.literature_genre = create_genre(code="90", name="文学")
        self.alpha_book = create_book(
            genre=self.tech_genre,
            isbn=VALID_ISBN,
            title="Alpha Cat Network",
            author="Natsume Alpha",
            publisher="Iwanami Alpha",
            published_date=date(1990, 4, 1),
            price=1200,
            cover_image_url=DEFAULT_COVER_IMAGE_URL,
            description="A story about cats and networks.",
        )
        self.beta_book = create_book(
            genre=self.literature_genre,
            isbn="9780975229804",
            title="Beta Library Design",
            author="Design Author",
            publisher="Beta Press",
            description="Library architecture guide.",
        )

    def get_book_list(self, params=None):
        return self.client.get(reverse("books:book-list"), params or {})

    def test_book_list_returns_paginated_response(self):
        response = self.get_book_list()

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(set(data.keys()), {"count", "next", "previous", "results"})
        self.assertEqual(data["count"], 2)
        self.assertEqual(data["next"], None)
        self.assertEqual(data["previous"], None)
        self.assertEqual(len(data["results"]), 2)

    def test_book_list_searches_by_keyword(self):
        response = self.get_book_list({"keyword": "Library"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual([book["title"] for book in response.json()["results"]], ["Beta Library Design"])

    def test_book_list_searches_by_title(self):
        response = self.get_book_list({"title": "Cat"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual([book["title"] for book in response.json()["results"]], ["Alpha Cat Network"])

    def test_book_list_searches_by_author(self):
        response = self.get_book_list({"author": "Design"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual([book["title"] for book in response.json()["results"]], ["Beta Library Design"])

    def test_book_list_searches_by_publisher(self):
        response = self.get_book_list({"publisher": "Iwanami"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual([book["title"] for book in response.json()["results"]], ["Alpha Cat Network"])

    def test_book_list_searches_by_normalized_isbn(self):
        response = self.get_book_list({"isbn": VALID_ISBN_WITH_HYPHENS})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["count"], 1)
        self.assertEqual(response.json()["results"][0]["isbn"], VALID_ISBN)

    def test_book_list_searches_by_genre(self):
        response = self.get_book_list({"genre": "55"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["count"], 1)
        self.assertEqual(response.json()["results"][0]["genre"]["c_code_genre"], "55")

    def test_book_list_returns_400_for_invalid_isbn(self):
        response = self.get_book_list({"isbn": INVALID_ISBN})

        self.assertEqual(response.status_code, 400)
        self.assertIn("isbn", response.json())

    def test_book_list_returns_400_for_unknown_genre(self):
        response = self.get_book_list({"genre": "99"})

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"genre": ["存在するジャンルを指定してください"]})

    def test_book_list_ignores_category_query_parameter(self):
        response = self.get_book_list({"category": "5", "category_code": "5"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["count"], 2)

    def test_book_list_returns_empty_results_for_no_matches(self):
        response = self.get_book_list({"keyword": "no-match"})

        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["count"], 0)
        self.assertEqual(data["results"], [])
        self.assertEqual(data["next"], None)
        self.assertEqual(data["previous"], None)

    def test_book_list_response_contains_book_and_genre_fields(self):
        response = self.get_book_list({"isbn": VALID_ISBN})

        book = response.json()["results"][0]
        self.assertEqual(
            set(book.keys()),
            {
                "id",
                "isbn",
                "title",
                "author",
                "publisher",
                "published_date",
                "price",
                "cover_image_url",
                "description",
                "genre",
            },
        )
        self.assertEqual(
            set(book["genre"].keys()),
            {"category_code", "category_name", "c_code_genre", "name"},
        )

    def test_book_detail_returns_book(self):
        response = self.client.get(reverse("books:book-detail", kwargs={"pk": self.alpha_book.pk}))

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["id"], str(self.alpha_book.id))
        self.assertEqual(data["title"], self.alpha_book.title)
        self.assertEqual(data["genre"]["c_code_genre"], "55")

    def test_book_detail_returns_404_for_unknown_book(self):
        response = self.client.get(reverse("books:book-detail", kwargs={"pk": uuid4()}))

        self.assertEqual(response.status_code, 404)


class BookSearchPaginationApiTests(TestCase):
    def get_book_list(self, params=None):
        return self.client.get(reverse("books:book-list"), params or {})

    def setUp(self):
        for index in range(12):
            create_book(
                isbn=f"97800000000{index:02d}",
                title=f"Book {index:02d}",
            )

    def test_book_list_uses_ten_items_per_page(self):
        response = self.get_book_list()
        data = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["count"], 12)
        self.assertEqual(len(data["results"]), 10)
        self.assertIn("page=2", data["next"])
        self.assertEqual(data["previous"], None)

    def test_book_list_can_return_second_page(self):
        response = self.get_book_list({"page": 2})
        data = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data["results"]), 2)
        self.assertIsNone(data["next"])
        self.assertIsNotNone(data["previous"])
