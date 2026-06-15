from dataclasses import dataclass

from django.db.models import Q, QuerySet

from books.models import Book

DEFAULT_BOOK_SEARCH_ORDERING = ("title", "id")
BOOK_SEARCH_TEXT_FIELDS = ("title", "author", "publisher", "isbn", "description")


@dataclass(frozen=True)
class BookSearchParams:
    keyword: str = ""
    title: str = ""
    author: str = ""
    publisher: str = ""
    isbn: str = ""
    genre: str = ""


def build_keyword_query(keyword: str) -> Q:
    """keyword を title / author / publisher / isbn / description の OR 条件にする。"""
    query = Q()
    for field in BOOK_SEARCH_TEXT_FIELDS:
        query |= Q(**{f"{field}__icontains": keyword})
    return query


def apply_book_search_filters(queryset: QuerySet[Book], params: BookSearchParams) -> QuerySet[Book]:
    """BookSearchParams に従って QuerySet へ検索条件を適用する。"""
    if params.keyword:
        queryset = queryset.filter(build_keyword_query(params.keyword))
    if params.title:
        queryset = queryset.filter(title__icontains=params.title)
    if params.author:
        queryset = queryset.filter(author__icontains=params.author)
    if params.publisher:
        queryset = queryset.filter(publisher__icontains=params.publisher)
    if params.isbn:
        queryset = queryset.filter(isbn=params.isbn)
    if params.genre:
        queryset = queryset.filter(genre_id=params.genre)
    return queryset


def search_books(params: BookSearchParams) -> QuerySet[Book]:
    """検索条件に一致する Book QuerySet を返す。"""
    queryset = Book.objects.select_related("genre")
    return apply_book_search_filters(queryset, params).order_by(*DEFAULT_BOOK_SEARCH_ORDERING)
