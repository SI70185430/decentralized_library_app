from django.test import TestCase
from django.urls import reverse

from books.forms import BookSearchForm
from books.genre_categories import GENRE_CATEGORY_NAMES
from books.models import Genre
from books.serializers import BookSearchQuerySerializer
from books.tests.helpers import (
    INVALID_ISBN,
    VALID_ISBN_WITH_HYPHENS,
    create_book,
    create_genre,
    create_staff_user,
)


class BookSearchFormTests(TestCase):
    def setUp(self):
        Genre.objects.all().delete()

    def test_form_fields_match_search_ui_inputs(self):
        form = BookSearchForm()

        self.assertEqual(
            list(form.fields),
            ["keyword", "title", "author", "publisher", "isbn", "category", "genre"],
        )

        expected_attrs = {
            "keyword": {"id": "input_keyword", "placeholder": "キーワード"},
            "title": {"id": "input_title", "placeholder": "タイトル"},
            "author": {"id": "input_author", "placeholder": "著者"},
            "publisher": {"id": "input_publisher", "placeholder": "出版社"},
            "isbn": {"id": "input_isbn", "placeholder": "ISBNコード"},
            "category": {"id": "input_category"},
            "genre": {"id": "input_genre"},
        }

        for field_name, attrs in expected_attrs.items():
            with self.subTest(field_name=field_name):
                self.assertEqual(form.fields[field_name].required, False)
                for attr_name, expected_value in attrs.items():
                    self.assertEqual(
                        form.fields[field_name].widget.attrs[attr_name], expected_value
                    )

    def test_category_choices_are_built_from_category_name_constants(self):
        form = BookSearchForm()

        self.assertEqual(
            form.fields["category"].choices,
            [
                ("", "すべて"),
                ("0", "総記"),
                ("1", "哲学"),
                ("2", "歴史"),
                ("3", "社会科学"),
                ("4", "自然科学"),
                ("5", "技術・工学"),
                ("6", "産業"),
                ("7", "芸術"),
                ("8", "言語"),
                ("9", "文学"),
            ],
        )

    def test_genre_choices_are_built_from_genres_ordered_by_code(self):
        create_genre(code="90", name="文学")
        create_genre(code="55", name="電気通信")
        create_genre(code="00", name="総記")

        form = BookSearchForm()

        self.assertEqual(
            form.fields["genre"].choices,
            [
                ("", "すべて"),
                ("00", "総記"),
                ("55", "電気通信"),
                ("90", "文学"),
            ],
        )

    def test_genre_choices_are_filtered_when_category_is_selected(self):
        create_genre(code="55", name="電気通信")
        create_genre(code="59", name="家政学")
        create_genre(code="90", name="文学")

        form = BookSearchForm(data={"category": "5"})

        self.assertEqual(
            form.fields["genre"].choices,
            [
                ("", "すべて"),
                ("55", "電気通信"),
                ("59", "家政学"),
            ],
        )

    def test_initial_category_filters_genre_choices_for_unbound_form(self):
        create_genre(code="55", name="電気通信")
        create_genre(code="90", name="文学")

        form = BookSearchForm(initial={"category": "9"})

        self.assertEqual(form.fields["genre"].choices, [("", "すべて"), ("90", "文学")])

    def test_search_query_data_excludes_category(self):
        create_genre(code="55", name="電気通信")

        form = BookSearchForm(
            data={
                "keyword": "  cats  ",
                "title": "  title  ",
                "author": "  author  ",
                "publisher": "  publisher  ",
                "isbn": VALID_ISBN_WITH_HYPHENS,
                "category": "5",
                "genre": "55",
            }
        )

        self.assertEqual(form.is_valid(), True, form.errors)
        self.assertEqual(
            form.search_query_data,
            {
                "keyword": "cats",
                "title": "title",
                "author": "author",
                "publisher": "publisher",
                "isbn": VALID_ISBN_WITH_HYPHENS,
                "genre": "55",
            },
        )

    def test_category_only_search_query_data_is_empty_values_without_category(self):
        form = BookSearchForm(data={"category": "5"})

        self.assertEqual(form.is_valid(), True, form.errors)
        self.assertEqual(
            form.search_query_data,
            {
                "keyword": "",
                "title": "",
                "author": "",
                "publisher": "",
                "isbn": "",
                "genre": "",
            },
        )

    def test_search_form_does_not_normalize_isbn(self):
        form = BookSearchForm(data={"isbn": VALID_ISBN_WITH_HYPHENS})

        self.assertEqual(form.is_valid(), True, form.errors)
        self.assertEqual(form.cleaned_data["isbn"], VALID_ISBN_WITH_HYPHENS)
        self.assertEqual(form.search_query_data["isbn"], VALID_ISBN_WITH_HYPHENS)

    def test_search_form_has_no_clean_isbn_override(self):
        self.assertFalse(hasattr(BookSearchForm, "clean_isbn"))

    def test_add_serializer_errors_adds_field_errors_to_form(self):
        form = BookSearchForm(data={"isbn": INVALID_ISBN})
        self.assertEqual(form.is_valid(), True, form.errors)

        serializer = BookSearchQuerySerializer(data=form.search_query_data)
        self.assertEqual(serializer.is_valid(), False)

        form.add_serializer_errors(serializer.errors)

        self.assertIn("isbn", form.errors)
        self.assertIn("10桁または13桁で正当なISBNを入力してください", form.errors["isbn"])

    def test_add_serializer_errors_adds_unknown_fields_as_non_field_errors(self):
        form = BookSearchForm(data={})
        self.assertEqual(form.is_valid(), True, form.errors)

        form.add_serializer_errors({"unknown": ["unknown error"]})

        self.assertIn("unknown error", form.non_field_errors())

    def test_genre_category_names_are_imported_from_shared_module(self):
        from books.serializers import GENRE_CATEGORY_NAMES as serializer_category_names

        self.assertIs(serializer_category_names, GENRE_CATEGORY_NAMES)


class BookSearchAdminViewTests(TestCase):
    def setUp(self):
        Genre.objects.all().delete()
        self.staff_user = create_staff_user(username="book-search-admin", employee_id=700010)

    def test_search_view_requires_staff_login(self):
        response = self.client.get(reverse("admin_books_search"))

        self.assertEqual(response.status_code, 302)
        self.assertIn("/admin/login/", response["Location"])

    def test_search_view_renders_form_for_staff_user(self):
        self.client.force_login(self.staff_user)

        response = self.client.get(reverse("admin_books_search"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "admin/books/search.html")
        self.assertContains(response, "書籍検索")
        self.assertContains(response, 'id="input_keyword"')
        self.assertContains(response, 'id="input_title"')
        self.assertContains(response, 'id="input_author"')
        self.assertContains(response, 'id="input_publisher"')
        self.assertContains(response, 'id="input_isbn"')
        self.assertContains(response, 'id="input_category"')
        self.assertContains(response, 'id="input_genre"')
        self.assertContains(response, 'id="btn_book_search"')
        self.assertContains(response, 'class="breadcrumb"')
        self.assertIsInstance(response.context["form"], BookSearchForm)

    def test_search_results_view_requires_staff_login(self):
        response = self.client.get(reverse("admin_books_search_results"))

        self.assertEqual(response.status_code, 302)
        self.assertIn("/admin/login/", response["Location"])

    def test_search_results_view_displays_matching_books(self):
        self.client.force_login(self.staff_user)
        tech_genre = create_genre(code="55", name="電気通信")
        literature_genre = create_genre(code="90", name="文学")
        create_book(
            genre=tech_genre,
            isbn="9784003101018",
            title="Alpha Cat Network",
            author="Natsume Alpha",
            publisher="Iwanami Alpha",
        )
        create_book(
            genre=literature_genre,
            isbn="9780975229804",
            title="Beta Library Design",
            author="Design Author",
            publisher="Beta Press",
        )

        response = self.client.get(reverse("admin_books_search_results"), {"keyword": "Library"})

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "admin/books/search_results.html")
        self.assertContains(response, "検索結果")
        self.assertContains(response, "Beta Library Design")
        self.assertNotContains(response, "Alpha Cat Network")
        self.assertEqual(response.context["page_obj"].paginator.count, 1)

    def test_search_results_view_displays_empty_message_for_no_matches(self):
        self.client.force_login(self.staff_user)
        create_book(isbn="9784003101018", title="Alpha Cat Network")

        response = self.client.get(reverse("admin_books_search_results"), {"keyword": "no-match"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "検索結果はありません。")
        self.assertEqual(response.context["page_obj"].paginator.count, 0)

    def test_search_results_view_displays_serializer_validation_errors(self):
        self.client.force_login(self.staff_user)
        create_book(isbn="9784003101018", title="Alpha Cat Network")

        response = self.client.get(reverse("admin_books_search_results"), {"isbn": INVALID_ISBN})

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "admin/books/search_results.html")
        self.assertContains(response, "10桁または13桁で正当なISBNを入力してください")
        self.assertContains(response, "検索結果はありません。")
        self.assertEqual(response.context["page_obj"].paginator.count, 0)

    def test_search_results_view_does_not_filter_by_category_only(self):
        self.client.force_login(self.staff_user)
        tech_genre = create_genre(code="55", name="電気通信")
        literature_genre = create_genre(code="90", name="文学")
        create_book(genre=tech_genre, isbn="9784003101018", title="Tech Book")
        create_book(genre=literature_genre, isbn="9780975229804", title="Literature Book")

        response = self.client.get(reverse("admin_books_search_results"), {"category": "5"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Tech Book")
        self.assertContains(response, "Literature Book")
        self.assertEqual(response.context["page_obj"].paginator.count, 2)

    def test_search_results_view_filters_genre_choices_by_selected_category(self):
        self.client.force_login(self.staff_user)
        create_genre(code="55", name="電気通信")
        create_genre(code="59", name="家政学")
        create_genre(code="90", name="文学")

        response = self.client.get(reverse("admin_books_search_results"), {"category": "5"})

        choices = response.context["form"].fields["genre"].choices
        self.assertEqual(choices, [("", "すべて"), ("55", "電気通信"), ("59", "家政学")])

    def test_search_results_view_uses_ten_items_per_page(self):
        self.client.force_login(self.staff_user)
        for index in range(12):
            create_book(isbn=f"97800000000{index:02d}", title=f"Book {index:02d}")

        response = self.client.get(reverse("admin_books_search_results"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["page_obj"].paginator.count, 12)
        self.assertEqual(len(response.context["page_obj"].object_list), 10)
        self.assertContains(response, "Book 00")
        self.assertContains(response, "Book 09")
        self.assertNotContains(response, "Book 10")
        self.assertContains(response, "page=2")

    def test_search_results_view_can_return_second_page(self):
        self.client.force_login(self.staff_user)
        for index in range(12):
            create_book(isbn=f"97800000000{index:02d}", title=f"Book {index:02d}")

        response = self.client.get(reverse("admin_books_search_results"), {"page": 2})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["page_obj"].object_list), 2)
        self.assertContains(response, "Book 10")
        self.assertContains(response, "Book 11")

    def test_search_results_pagination_links_keep_query_parameters(self):
        self.client.force_login(self.staff_user)
        for index in range(12):
            create_book(isbn=f"97800000000{index:02d}", title=f"Cat Book {index:02d}")

        response = self.client.get(reverse("admin_books_search_results"), {"title": "Cat"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "title=Cat&amp;page=2")


class BookSearchAdminNavigationTests(TestCase):
    def setUp(self):
        self.staff_user = create_staff_user(
            username="book-search-navigation-admin",
            employee_id=700011,
        )

    def test_admin_header_links_to_book_search_view(self):
        self.client.force_login(self.staff_user)

        response = self.client.get(reverse("admin:index"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "書籍検索", count=1)
        self.assertContains(response, f'href="{reverse("admin_books_search")}"', count=1)
