from datetime import date
from typing import Any

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_GET

from books.forms import BookRegisterForm, BookSearchForm
from books.models import Book
from books.serializers import BookSearchQuerySerializer
from books.services.book_registration import register_book_copies
from books.services.book_search import search_books
from books.services.openbd import OpenBdError, lookup_book_info_by_isbn

LOOKUP_NOT_FOUND_MESSAGE = "書籍情報が見つかりませんでした"
OPENBD_LOOKUP_ERROR_MESSAGE = "openBDから書籍情報を取得できませんでした"
REGISTER_SUCCESS_MESSAGE = "蔵書を登録しました"
REGISTER_PAGE_TITLE = "書籍登録"
REGISTER_TEMPLATE_NAME = "admin/books/register.html"
ADMIN_BOOK_REGISTER_ROUTE_NAME = "admin_books_register"
BOOK_SEARCH_PAGE_SIZE = 10
SEARCH_PAGE_TITLE = "書籍検索"
SEARCH_RESULTS_PAGE_TITLE = "書籍検索結果"
SEARCH_TEMPLATE_NAME = "admin/books/search.html"
SEARCH_RESULTS_TEMPLATE_NAME = "admin/books/search_results.html"
ADMIN_BOOK_SEARCH_ROUTE_NAME = "admin_books_search"
ADMIN_BOOK_SEARCH_RESULTS_ROUTE_NAME = "admin_books_search_results"
VALIDATION_DEFAULT_ERROR_MESSAGE = "入力内容を確認してください"
ISBN_QUERY_PARAM = "isbn"
JSON_ERROR_KEY = "error"
JSON_BOOK_KEY = "book"


def book_register(request: HttpRequest) -> HttpResponse:
    """管理画面の書籍登録専用画面を表示し、登録処理を行う。"""
    if request.method == "POST":
        form = BookRegisterForm(request.POST)
        if form.is_valid():
            result = register_book_copies(form.cleaned_data)
            messages.success(
                request,
                f"{REGISTER_SUCCESS_MESSAGE}（{result.book.title} / {len(result.copies)}冊）",
            )
            return redirect(ADMIN_BOOK_REGISTER_ROUTE_NAME)
    else:
        form = BookRegisterForm()

    return render(
        request,  # ログインユーザー情報、CSRF情報等を利用
        REGISTER_TEMPLATE_NAME,
        {
            "form": form,
            "title": REGISTER_PAGE_TITLE,
            "opts": Book._meta,  # admin テンプレート用のデータ、構造的互換性のために記述
        },
    )


def book_search(request: HttpRequest) -> HttpResponse:
    """管理画面の書籍検索専用フォーム画面を表示する。"""
    return render(
        request,
        SEARCH_TEMPLATE_NAME,
        {
            "form": BookSearchForm(),
            "title": SEARCH_PAGE_TITLE,
            "opts": Book._meta,
        },
    )


def book_search_results(request: HttpRequest) -> HttpResponse:
    """管理画面の書籍検索結果をページネーション付きで表示する。"""
    form = BookSearchForm(data=request.GET)
    queryset = Book.objects.none()

    if form.is_valid():
        query_serializer = BookSearchQuerySerializer(data=form.search_query_data)
        if query_serializer.is_valid():
            queryset = search_books(query_serializer.to_params())
        else:
            form.add_serializer_errors(query_serializer.errors)

    paginator = Paginator(queryset, BOOK_SEARCH_PAGE_SIZE)
    page_obj = paginator.get_page(request.GET.get("page"))
    querystring_without_page = _querystring_without_page(request)

    return render(
        request,
        SEARCH_RESULTS_TEMPLATE_NAME,
        {
            "form": form,
            "page_obj": page_obj,
            "paginator": paginator,
            "querystring_without_page": querystring_without_page,
            "pagination_query_prefix": _pagination_query_prefix(querystring_without_page),
            "title": SEARCH_RESULTS_PAGE_TITLE,
            "opts": Book._meta,
        },
    )


@require_GET
def isbn_lookup(request: HttpRequest) -> JsonResponse:
    """管理画面向けにISBNから書籍登録フォームの値を返す。"""
    isbn = request.GET.get(ISBN_QUERY_PARAM, "")

    try:
        book_data = lookup_book_info_by_isbn(isbn)
    except ValidationError as error:
        return JsonResponse({JSON_ERROR_KEY: _validation_error_message(error)}, status=400)
    except OpenBdError:
        return JsonResponse({JSON_ERROR_KEY: OPENBD_LOOKUP_ERROR_MESSAGE}, status=502)

    if book_data is None:
        return JsonResponse({JSON_ERROR_KEY: LOOKUP_NOT_FOUND_MESSAGE}, status=404)

    return JsonResponse({JSON_BOOK_KEY: _serialize_lookup_data(book_data)})


def _querystring_without_page(request: HttpRequest) -> str:
    query_params = request.GET.copy()
    query_params.pop("page", None)
    return query_params.urlencode()


def _pagination_query_prefix(querystring_without_page: str) -> str:
    if not querystring_without_page:
        return ""

    return f"{querystring_without_page}&"


def _serialize_lookup_data(data: dict[str, Any]) -> dict[str, Any]:
    return {
        "isbn": data["isbn"],
        "title": data["title"],
        "author": data["author"],
        "publisher": data["publisher"],
        "published_date": _serialize_date(data["published_date"]),
        "cover_image_url": data["cover_image_url"],
        "price": data["price"],
        "genre_code": data["genre_code"],
    }


def _serialize_date(value: date | None) -> str:
    if value is None:
        return ""

    return value.isoformat()


def _validation_error_message(error: ValidationError) -> str:
    if error.messages:
        return str(error.messages[0])

    return VALIDATION_DEFAULT_ERROR_MESSAGE
