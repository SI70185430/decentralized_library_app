from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from books.models import Book, Genre
from books.serializers import (
    BookDetailSerializer,
    BookListSerializer,
    BookSearchQuerySerializer,
    GenreSerializer,
)
from books.services.book_search import search_books


class BookPagination(PageNumberPagination):
    page_size = 10


# OpenAPI / Swagger 用に「ページネーション付き書籍一覧レスポンス」の形を定義
PaginatedBookListResponseSerializer = inline_serializer(
    name="PaginatedBookListResponse",
    fields={
        "count": serializers.IntegerField(),
        "next": serializers.URLField(allow_null=True),
        "previous": serializers.URLField(allow_null=True),
        "results": BookListSerializer(many=True),
    },
)


class BookListView(APIView):
    @extend_schema(
        operation_id="books_list",
        parameters=[BookSearchQuerySerializer],
        responses={200: PaginatedBookListResponseSerializer},
    )
    def get(self, request):
        query_serializer = BookSearchQuerySerializer(data=request.query_params)
        query_serializer.is_valid(raise_exception=True)

        queryset = search_books(query_serializer.to_params())
        paginator = BookPagination()
        page = paginator.paginate_queryset(queryset, request, view=self)
        serializer = BookListSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)


class GenreListView(APIView):
    @extend_schema(operation_id="book_genres_list", responses={200: GenreSerializer(many=True)})
    def get(self, request):
        queryset = Genre.objects.order_by("c_code_genre")
        serializer = GenreSerializer(queryset, many=True)
        return Response(serializer.data)


class BookDetailView(APIView):
    @extend_schema(operation_id="books_retrieve", responses={200: BookDetailSerializer})
    def get(self, request, pk):
        book = get_object_or_404(Book.objects.select_related("genre"), pk=pk)
        serializer = BookDetailSerializer(book, context={"request": request})
        return Response(serializer.data)
