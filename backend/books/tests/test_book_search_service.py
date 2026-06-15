from django.db import connection
from django.test import TestCase
from django.test.utils import CaptureQueriesContext

from books.services.book_search import BookSearchParams, search_books
from books.tests.helpers import create_book, create_genre


class BookSearchServiceTests(TestCase):
    def setUp(self):
        self.tech_genre = create_genre(code="55", name="電気通信")
        self.literature_genre = create_genre(code="90", name="文学")

        self.alpha_book = create_book(
            genre=self.tech_genre,
            isbn="9784003101018",
            title="Alpha Cat Network",
            author="Natsume Alpha",
            publisher="Iwanami Alpha",
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
        self.gamma_book = create_book(
            isbn="9784101010014",
            title="Gamma No Genre",
            author=None,
            publisher=None,
            description=None,
        )

    def test_search_books_without_params_returns_all_books_ordered_by_title_and_id(self):
        books = list(search_books(BookSearchParams()))

        self.assertEqual(books, [self.alpha_book, self.beta_book, self.gamma_book])

    def test_keyword_matches_title(self):
        self.assertEqual(list(search_books(BookSearchParams(keyword="cat"))), [self.alpha_book])

    def test_keyword_matches_author(self):
        self.assertEqual(
            list(search_books(BookSearchParams(keyword="Design Author"))),
            [self.beta_book],
        )

    def test_keyword_matches_publisher(self):
        self.assertEqual(
            list(search_books(BookSearchParams(keyword="Beta Press"))),
            [self.beta_book],
        )

    def test_keyword_matches_isbn(self):
        self.assertEqual(
            list(search_books(BookSearchParams(keyword="9780975229804"))),
            [self.beta_book],
        )

    def test_keyword_matches_description(self):
        self.assertEqual(list(search_books(BookSearchParams(keyword="networks"))), [self.alpha_book])

    def test_title_filter_uses_partial_match(self):
        self.assertEqual(list(search_books(BookSearchParams(title="Library"))), [self.beta_book])

    def test_author_filter_uses_partial_match(self):
        self.assertEqual(list(search_books(BookSearchParams(author="Natsume"))), [self.alpha_book])

    def test_publisher_filter_uses_partial_match(self):
        self.assertEqual(
            list(search_books(BookSearchParams(publisher="Iwanami"))),
            [self.alpha_book],
        )

    def test_isbn_filter_uses_exact_match(self):
        self.assertEqual(
            list(search_books(BookSearchParams(isbn="9784003101018"))),
            [self.alpha_book],
        )

    def test_isbn_filter_does_not_use_partial_match(self):
        self.assertEqual(list(search_books(BookSearchParams(isbn="978400"))), [])

    def test_genre_filter_uses_genre_code_exact_match(self):
        self.assertEqual(list(search_books(BookSearchParams(genre="55"))), [self.alpha_book])
        self.assertEqual(list(search_books(BookSearchParams(genre="90"))), [self.beta_book])

    def test_genre_filter_returns_empty_for_unknown_code_without_validation(self):
        self.assertEqual(list(search_books(BookSearchParams(genre="99"))), [])

    def test_multiple_filters_are_combined_with_and(self):
        self.assertEqual(
            list(search_books(BookSearchParams(keyword="Library", publisher="Beta Press"))),
            [self.beta_book],
        )
        self.assertEqual(
            list(search_books(BookSearchParams(keyword="Library", publisher="Iwanami"))),
            [],
        )

    def test_keyword_and_individual_filter_are_combined_with_and(self):
        self.assertEqual(
            list(search_books(BookSearchParams(title="Alpha", genre="55"))),
            [self.alpha_book],
        )
        self.assertEqual(
            list(search_books(BookSearchParams(title="Alpha", genre="90"))),
            [],
        )

    def test_empty_string_params_are_ignored(self):
        params = BookSearchParams(
            keyword="",
            title="",
            author="",
            publisher="",
            isbn="",
            genre="",
        )

        self.assertEqual(list(search_books(params)), [self.alpha_book, self.beta_book, self.gamma_book])

    def test_book_search_params_does_not_accept_category(self):
        with self.assertRaises(TypeError):
            BookSearchParams(category="5")

    def test_search_books_selects_related_genre(self):
        with CaptureQueriesContext(connection) as captured_queries:
            books = list(search_books(BookSearchParams(genre="55")))
            genre_names = [book.genre.name for book in books]

        self.assertEqual(genre_names, ["電気通信"])
        self.assertEqual(len(captured_queries), 1)
