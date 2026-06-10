from datetime import date
from typing import Any

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_GET

from books.forms import BookRegisterForm
from books.models import Book
from books.services.book_registration import register_book_copies
from books.services.openbd import OpenBdError, lookup_book_info_by_isbn

LOOKUP_NOT_FOUND_MESSAGE = "書籍情報が見つかりませんでした"
OPENBD_LOOKUP_ERROR_MESSAGE = "openBDから書籍情報を取得できませんでした"
REGISTER_SUCCESS_MESSAGE = "蔵書を登録しました"


def book_register(request: HttpRequest) -> HttpResponse:
    """Render and process the dedicated admin book registration screen."""
    if request.method == "POST":
        form = BookRegisterForm(request.POST)
        if form.is_valid():
            result = register_book_copies(form.cleaned_data)
            messages.success(
                request,
                f"{REGISTER_SUCCESS_MESSAGE}（{result.book.title} / {len(result.copies)}冊）",
            )
            return redirect("admin_books_register")
    else:
        form = BookRegisterForm()

    return render(
        request, # ログインユーザー情報、CSRF情報等を利用
        "admin/books/register.html",
        {
            "form": form,
            "title": "書籍登録",
            "opts": Book._meta, # admin テンプレート用のデータ、構造的互換性のために記述
        },
    )


@require_GET
def isbn_lookup(request: HttpRequest) -> JsonResponse:
    """Return book registration form values by ISBN for the admin screen."""
    isbn = request.GET.get("isbn", "")

    try:
        book_data = lookup_book_info_by_isbn(isbn)
    except ValidationError as error:
        return JsonResponse({"error": _validation_error_message(error)}, status=400)
    except OpenBdError:
        return JsonResponse({"error": OPENBD_LOOKUP_ERROR_MESSAGE}, status=502)

    if book_data is None:
        return JsonResponse({"error": LOOKUP_NOT_FOUND_MESSAGE}, status=404)

    return JsonResponse({"book": _serialize_lookup_data(book_data)})


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

    return "入力内容を確認してください"
