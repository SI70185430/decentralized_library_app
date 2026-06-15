from django import forms

from books.genre_categories import GENRE_CATEGORY_NAMES
from books.models import Genre

SEARCH_KEYWORD_INPUT_ID = "input_keyword"
SEARCH_TITLE_INPUT_ID = "input_title"
SEARCH_AUTHOR_INPUT_ID = "input_author"
SEARCH_PUBLISHER_INPUT_ID = "input_publisher"
SEARCH_ISBN_INPUT_ID = "input_isbn"
SEARCH_CATEGORY_INPUT_ID = "input_category"
SEARCH_GENRE_INPUT_ID = "input_genre"

SEARCH_KEYWORD_PLACEHOLDER = "キーワード"
SEARCH_TITLE_PLACEHOLDER = "タイトル"
SEARCH_AUTHOR_PLACEHOLDER = "著者"
SEARCH_PUBLISHER_PLACEHOLDER = "出版社"
SEARCH_ISBN_PLACEHOLDER = "ISBNコード"

BOOK_SEARCH_ALL_CHOICE_LABEL = "すべて"
BOOK_SEARCH_QUERY_FIELDS = ("keyword", "title", "author", "publisher", "isbn", "genre")


def build_category_choices() -> list[tuple[str, str]]:
    return [("", BOOK_SEARCH_ALL_CHOICE_LABEL), *GENRE_CATEGORY_NAMES.items()]


def build_genre_choices(*, category: str = "") -> list[tuple[str, str]]:
    queryset = Genre.objects.order_by("c_code_genre")
    if category:
        queryset = queryset.filter(c_code_genre__startswith=category)

    return [
        ("", BOOK_SEARCH_ALL_CHOICE_LABEL),
        *((genre.c_code_genre, genre.name) for genre in queryset),
    ]


class BookSearchForm(forms.Form):
    keyword = forms.CharField(
        label="キーワード",
        required=False,
        widget=forms.TextInput(
            attrs={"id": SEARCH_KEYWORD_INPUT_ID, "placeholder": SEARCH_KEYWORD_PLACEHOLDER}
        ),
    )
    title = forms.CharField(
        label="タイトル",
        required=False,
        widget=forms.TextInput(
            attrs={"id": SEARCH_TITLE_INPUT_ID, "placeholder": SEARCH_TITLE_PLACEHOLDER}
        ),
    )
    author = forms.CharField(
        label="著者",
        required=False,
        widget=forms.TextInput(
            attrs={"id": SEARCH_AUTHOR_INPUT_ID, "placeholder": SEARCH_AUTHOR_PLACEHOLDER}
        ),
    )
    publisher = forms.CharField(
        label="出版社名",
        required=False,
        widget=forms.TextInput(
            attrs={"id": SEARCH_PUBLISHER_INPUT_ID, "placeholder": SEARCH_PUBLISHER_PLACEHOLDER}
        ),
    )
    isbn = forms.CharField(
        label="ISBNコード",
        required=False,
        widget=forms.TextInput(
            attrs={"id": SEARCH_ISBN_INPUT_ID, "placeholder": SEARCH_ISBN_PLACEHOLDER}
        ),
    )
    category = forms.ChoiceField(
        label="大分類",
        required=False,
        choices=(),
        widget=forms.Select(attrs={"id": SEARCH_CATEGORY_INPUT_ID}),
    )
    genre = forms.ChoiceField(
        label="ジャンル",
        required=False,
        choices=(),
        widget=forms.Select(attrs={"id": SEARCH_GENRE_INPUT_ID}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        category = self._selected_category()
        self.fields["category"].choices = build_category_choices()
        self.fields["genre"].choices = build_genre_choices(category=category)

    @property
    def search_query_data(self) -> dict[str, str]:
        return {field: self.cleaned_data.get(field, "") for field in BOOK_SEARCH_QUERY_FIELDS}

    def add_serializer_errors(self, errors) -> None:
        for field_name, field_errors in errors.items():
            target_field = field_name if field_name in self.fields else None
            for error in field_errors:
                self.add_error(target_field, str(error))

    def _selected_category(self) -> str:
        value = self.data.get("category", "") if self.is_bound else self.initial.get("category", "")
        return value if isinstance(value, str) else ""
