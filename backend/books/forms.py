from django import forms
from django.core.exceptions import ValidationError

from books.models import Genre
from books.services.openbd import normalize_isbn13

GENRE_CODE_ERROR_MESSAGE = "存在するCコードを入力してください"
PRICE_MIN_ERROR_MESSAGE = "0以上を入力して下さい"
PRICE_MAX_ERROR_MESSAGE = "9,999,999以下を入力してください"
COPY_COUNT_MIN_ERROR_MESSAGE = "1以上を入力して下さい"
COPY_COUNT_MAX_ERROR_MESSAGE = "100以下を入力してください"
MAX_BOOK_PRICE = 9999999
MAX_BOOK_COPY_COUNT = 100

ISBN_INPUT_ID = "input_isbn"
TITLE_INPUT_ID = "input_title"
AUTHOR_INPUT_ID = "input_author"
PUBLISHER_INPUT_ID = "input_publisher"
PUBLISHED_DATE_INPUT_ID = "input_publication_date"
COVER_IMAGE_URL_INPUT_ID = "input_image_url"
PRICE_INPUT_ID = "input_price"
GENRE_CODE_INPUT_ID = "input_ccode"
PURCHASE_DATE_INPUT_ID = "input_purchase_date"
LOCATION_INPUT_ID = "input_location"
COPY_COUNT_INPUT_ID = "input_num_of_books"

ISBN_PLACEHOLDER = "ISBNコード"
TITLE_PLACEHOLDER = "タイトル"
AUTHOR_PLACEHOLDER = "著者"
PUBLISHER_PLACEHOLDER = "出版社"
PUBLISHED_DATE_PLACEHOLDER = "出版日"
COVER_IMAGE_URL_PLACEHOLDER = "画像用リンク"
PRICE_PLACEHOLDER = "価格"
GENRE_CODE_PLACEHOLDER = "Cコード"
LOCATION_PLACEHOLDER = "保管場所"
COPY_COUNT_PLACEHOLDER = "版数"


class BookRegisterForm(forms.Form):
    isbn = forms.CharField(
        label="ISBNコード",
        max_length=20,
        widget=forms.TextInput(attrs={"id": ISBN_INPUT_ID, "placeholder": ISBN_PLACEHOLDER}),
    )
    title = forms.CharField(
        label="タイトル",
        max_length=255,
        widget=forms.TextInput(attrs={"id": TITLE_INPUT_ID, "placeholder": TITLE_PLACEHOLDER}),
    )
    author = forms.CharField(
        label="著者",
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={"id": AUTHOR_INPUT_ID, "placeholder": AUTHOR_PLACEHOLDER}),
    )
    publisher = forms.CharField(
        label="出版社名",
        max_length=255,
        required=False,
        widget=forms.TextInput(
            attrs={"id": PUBLISHER_INPUT_ID, "placeholder": PUBLISHER_PLACEHOLDER}
        ),
    )
    published_date = forms.DateField(
        label="出版日",
        required=False,
        input_formats=["%Y-%m-%d"],
        widget=forms.TextInput(
            attrs={"id": PUBLISHED_DATE_INPUT_ID, "placeholder": PUBLISHED_DATE_PLACEHOLDER}
        ),
    )
    cover_image_url = forms.URLField(
        label="画像用リンク",
        max_length=500,
        required=False,
        widget=forms.URLInput(
            attrs={"id": COVER_IMAGE_URL_INPUT_ID, "placeholder": COVER_IMAGE_URL_PLACEHOLDER}
        ),
    )
    price = forms.IntegerField(
        label="価格",
        min_value=0,
        max_value=MAX_BOOK_PRICE,
        required=False,
        error_messages={
            "min_value": PRICE_MIN_ERROR_MESSAGE,
            "max_value": PRICE_MAX_ERROR_MESSAGE,
        },
        widget=forms.NumberInput(attrs={"id": PRICE_INPUT_ID, "placeholder": PRICE_PLACEHOLDER}),
    )
    genre_code = forms.CharField(
        label="Cコード",
        max_length=2,
        required=False,
        widget=forms.TextInput(
            attrs={"id": GENRE_CODE_INPUT_ID, "placeholder": GENRE_CODE_PLACEHOLDER}
        ),
    )
    purchase_date = forms.DateField(
        label="購入日",
        required=False,
        input_formats=["%Y-%m-%d"],
        widget=forms.DateInput(
            format="%Y-%m-%d",
            attrs={"id": PURCHASE_DATE_INPUT_ID, "type": "date"},
        ),
    )
    location = forms.CharField(
        label="保管場所",
        max_length=255,
        widget=forms.TextInput(
            attrs={"id": LOCATION_INPUT_ID, "placeholder": LOCATION_PLACEHOLDER}
        ),
    )
    copy_count = forms.IntegerField(
        label="版数",
        min_value=1,
        max_value=MAX_BOOK_COPY_COUNT,
        error_messages={
            "min_value": COPY_COUNT_MIN_ERROR_MESSAGE,
            "max_value": COPY_COUNT_MAX_ERROR_MESSAGE,
        },
        widget=forms.NumberInput(
            attrs={
                "id": COPY_COUNT_INPUT_ID,
                "placeholder": COPY_COUNT_PLACEHOLDER,
                "inputmode": "numeric",
            }
        ),
    )

    def clean_isbn(self) -> str:
        return normalize_isbn13(self.cleaned_data["isbn"])

    def clean_genre_code(self) -> str:
        genre_code = self.cleaned_data["genre_code"]
        if not genre_code:
            return ""

        if not Genre.objects.filter(c_code_genre=genre_code).exists():
            raise ValidationError(GENRE_CODE_ERROR_MESSAGE)

        return genre_code
