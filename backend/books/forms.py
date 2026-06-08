from django import forms
from django.core.exceptions import ValidationError

from books.models import Genre
from books.services.openbd import normalize_isbn13

GENRE_CODE_ERROR_MESSAGE = "存在するCコードを入力してください"


class BookRegisterForm(forms.Form):
    isbn = forms.CharField(
        label="ISBNコード",
        max_length=20,
        widget=forms.TextInput(attrs={"id": "input_isbn", "placeholder": "ISBNコード"}),
    )
    title = forms.CharField(
        label="タイトル",
        max_length=255,
        widget=forms.TextInput(attrs={"id": "input_title", "placeholder": "タイトル"}),
    )
    author = forms.CharField(
        label="著者",
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={"id": "input_author", "placeholder": "著者"}),
    )
    publisher = forms.CharField(
        label="出版社名",
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={"id": "input_publisher", "placeholder": "出版社"}),
    )
    published_date = forms.DateField(
        label="出版日",
        required=False,
        input_formats=["%Y-%m-%d"],
        widget=forms.TextInput(attrs={"id": "input_publication_date", "placeholder": "出版日"}),
    )
    cover_image_url = forms.URLField(
        label="画像用リンク",
        max_length=500,
        required=False,
        widget=forms.URLInput(attrs={"id": "input_image_url", "placeholder": "画像用リンク"}),
    )
    price = forms.IntegerField(
        label="価格",
        min_value=0,
        required=False,
        widget=forms.NumberInput(attrs={"id": "input_price", "placeholder": "価格"}),
    )
    genre_code = forms.CharField(
        label="Cコード",
        max_length=2,
        required=False,
        widget=forms.TextInput(attrs={"id": "input_ccode", "placeholder": "Cコード"}),
    )
    purchase_date = forms.DateField(
        label="購入日",
        required=False,
        input_formats=["%Y-%m-%d"],
        widget=forms.TextInput(attrs={"id": "input_purchase_date", "placeholder": "購入日"}),
    )
    location = forms.CharField(
        label="保管場所",
        max_length=255,
        widget=forms.TextInput(attrs={"id": "input_location", "placeholder": "保管場所"}),
    )
    copy_count = forms.IntegerField(
        label="版数",
        min_value=1,
        widget=forms.NumberInput(
            attrs={"id": "input_num_of_books", "placeholder": "版数", "inputmode": "numeric"}
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
