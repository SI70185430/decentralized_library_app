from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from books.genre_categories import GENRE_CATEGORY_NAMES
from books.models import Book, Genre
from books.services.book_search import BookSearchParams
from books.services.isbn import normalize_isbn

GENRE_ERROR_MESSAGE = "存在するジャンルを指定してください"
SEARCH_PARAM_FIELDS = ("keyword", "title", "author", "publisher", "isbn", "genre")


class BookSearchQuerySerializer(serializers.Serializer):
    keyword = serializers.CharField(required=False, allow_blank=True, trim_whitespace=True)
    title = serializers.CharField(required=False, allow_blank=True, trim_whitespace=True)
    author = serializers.CharField(required=False, allow_blank=True, trim_whitespace=True)
    publisher = serializers.CharField(required=False, allow_blank=True, trim_whitespace=True)
    isbn = serializers.CharField(required=False, allow_blank=True, trim_whitespace=True)
    genre = serializers.CharField(required=False, allow_blank=True, trim_whitespace=True)

    def validate_isbn(self, value: str) -> str:
        if not value:
            return ""

        try:
            return normalize_isbn(value)
        except DjangoValidationError as error:
            raise serializers.ValidationError(error.messages) from error

    def validate_genre(self, value: str) -> str:
        if not value:
            return ""

        if not Genre.objects.filter(c_code_genre=value).exists():
            raise serializers.ValidationError(GENRE_ERROR_MESSAGE)

        return value

    def to_params(self) -> BookSearchParams:
        return BookSearchParams(
            **{field: self.validated_data.get(field, "") for field in SEARCH_PARAM_FIELDS}
        )


class GenreSerializer(serializers.ModelSerializer):
    category_code = serializers.SerializerMethodField()
    category_name = serializers.SerializerMethodField()

    class Meta:
        model = Genre
        fields = ["category_code", "category_name", "c_code_genre", "name"]

    def get_category_code(self, obj: Genre) -> str:
        return obj.c_code_genre[:1]

    def get_category_name(self, obj: Genre) -> str:
        return GENRE_CATEGORY_NAMES.get(obj.c_code_genre[:1], "")


class BookListSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(read_only=True)

    class Meta:
        model = Book
        fields = [
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
        ]


class BookDetailSerializer(BookListSerializer):
    pass
