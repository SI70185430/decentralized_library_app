from dataclasses import asdict

from django.core.exceptions import ValidationError as DjangoValidationError
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from books.genre_categories import GENRE_CATEGORY_NAMES
from books.models import Book, Genre
from books.services.book_detail import build_book_detail_state
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

        # htmlのみで仮UIを作成した都合で生じたエラーチェック
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


class BookAvailabilitySerializer(serializers.Serializer):
    status_code = serializers.CharField()
    status_label = serializers.CharField()
    available_copy_count = serializers.IntegerField()
    current_lending_id = serializers.UUIDField(allow_null=True)
    current_reservation_id = serializers.UUIDField(allow_null=True)


class BookActionSerializer(serializers.Serializer):
    type = serializers.CharField()
    label = serializers.CharField()
    method = serializers.CharField()
    endpoint = serializers.CharField()
    request_body = serializers.DictField(child=serializers.CharField(), allow_empty=True)
    enabled = serializers.BooleanField()


class BookActionsSerializer(serializers.Serializer):
    primary = BookActionSerializer(allow_null=True)
    secondary = BookActionSerializer(allow_null=True)


class BookDetailSerializer(BookListSerializer):
    availability = serializers.SerializerMethodField()
    actions = serializers.SerializerMethodField()

    class Meta(BookListSerializer.Meta):
        fields = [*BookListSerializer.Meta.fields, "availability", "actions"]

    @extend_schema_field(BookAvailabilitySerializer)
    def get_availability(self, obj: Book) -> dict:
        return asdict(self._get_detail_state(obj).availability)

    @extend_schema_field(BookActionsSerializer)
    def get_actions(self, obj: Book) -> dict:
        state = self._get_detail_state(obj)
        return {
            "primary": asdict(state.primary_action) if state.primary_action is not None else None,
            "secondary": asdict(state.secondary_action)
            if state.secondary_action is not None
            else None,
        }

    def _get_detail_state(self, obj: Book):
        if not hasattr(self, "_book_detail_state"):
            request = self.context.get("request")
            user = request.user if request is not None else None
            self._book_detail_state = build_book_detail_state(obj, user)

        return self._book_detail_state
