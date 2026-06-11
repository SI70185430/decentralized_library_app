import json
import re
import urllib.error
import urllib.parse
import urllib.request
from datetime import date
from typing import Any  # 外部APIを扱う関係でAnyを許容

from django.core.exceptions import ValidationError

from books.models import Book

ISBN_ERROR_MESSAGE = "10桁または13桁で正当なISBNを入力してください"
OPENBD_ENDPOINT = "https://api.openbd.jp/v1/get"
OPENBD_TIMEOUT_SECONDS = 10


class OpenBdError(Exception):
    """openBD lookup failed due to network or response errors."""


def normalize_isbn(value: str) -> str:
    """Normalize a user-entered ISBN value to ISBN-13 digits."""
    # 何かの間違いでNone等を受け取ってしまったときのためのor ""、xを大文字に統一して扱うための.upper()
    normalized = re.sub(r"[-\s]", "", value or "").upper()

    if re.fullmatch(r"\d{13}", normalized):
        if not is_valid_isbn13(normalized):
            raise ValidationError(ISBN_ERROR_MESSAGE)
        return normalized

    if re.fullmatch(r"\d{9}[\dX]", normalized):
        if not is_valid_isbn10(normalized):
            raise ValidationError(ISBN_ERROR_MESSAGE)
        return convert_isbn10_to_isbn13(normalized)

    raise ValidationError(ISBN_ERROR_MESSAGE)


def is_valid_isbn10(value: str) -> bool:
    """Return whether a normalized ISBN-10 has a valid check digit."""
    total = 0
    for index, char in enumerate(value):
        digit = 10 if char == "X" else int(char)
        total += digit * (10 - index)

    return total % 11 == 0


def is_valid_isbn13(value: str) -> bool:
    """Return whether a normalized ISBN-13 has a valid check digit."""
    return calculate_isbn13_check_digit(value[:12]) == int(value[12])


def convert_isbn10_to_isbn13(value: str) -> str:
    """Convert a normalized ISBN-10 into ISBN-13."""
    prefix_body = f"978{value[:9]}"
    check_digit = calculate_isbn13_check_digit(prefix_body)
    return f"{prefix_body}{check_digit}"


def calculate_isbn13_check_digit(value: str) -> int:
    """Calculate an ISBN-13 check digit from the first 12 digits."""
    total = sum(int(digit) * (1 if index % 2 == 0 else 3) for index, digit in enumerate(value))
    return (10 - total % 10) % 10


def parse_openbd_pubdate(value: str | None) -> date | None:
    """Convert openBD summary.pubdate into a date for Book.published_date."""
    if not value:
        return None

    normalized = value.strip()

    try:
        if re.fullmatch(r"\d{4}", normalized):
            return date(int(normalized), 1, 1)

        if re.fullmatch(r"\d{6}", normalized):
            return date(int(normalized[:4]), int(normalized[4:6]), 1)

        if re.fullmatch(r"\d{8}", normalized):
            return date(
                int(normalized[:4]),
                int(normalized[4:6]),
                int(normalized[6:8]),
            )
    except ValueError:
        return None

    return None


def fetch_openbd_book_data(isbn: str) -> dict[str, Any] | None:
    """Fetch an openBD book data object by normalized ISBN-13."""
    query = urllib.parse.urlencode({"isbn": isbn})
    url = f"{OPENBD_ENDPOINT}?{query}"

    try:
        with urllib.request.urlopen(url, timeout=OPENBD_TIMEOUT_SECONDS) as response:
            data = json.load(response)
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as error:
        raise OpenBdError("openBDから書籍情報を取得できませんでした") from error

    # レスポンスの中身が[null]ではなく[]だった場合の保険のnot data
    if not data or data[0] is None:
        return None

    # .get()でエラーを吐かないように型の保証
    openbd_data = data[0]
    if not isinstance(openbd_data, dict):
        return None

    summary = openbd_data.get("summary")
    if not isinstance(summary, dict) or not summary:
        return None

    return openbd_data


def map_openbd_book_data(openbd_data: dict[str, Any], normalized_isbn: str) -> dict[str, Any]:
    """Map openBD book data into book registration lookup data."""
    summary = openbd_data["summary"]
    return {
        "isbn": normalized_isbn,
        "title": summary.get("title") or "",
        "author": summary.get("author") or "",
        "publisher": summary.get("publisher") or "",
        "published_date": parse_openbd_pubdate(summary.get("pubdate")),
        "cover_image_url": summary.get("cover") or "",
        "price": extract_openbd_price(openbd_data),
        "genre_code": "",  # フォームを更新時にクリアするときにこの空文字を利用
    }


def extract_openbd_price(openbd_data: dict[str, Any]) -> int | None:
    """Extract a price amount from openBD ONIX data."""
    prices = (
        (openbd_data.get("onix") or {})
        .get("ProductSupply", {})
        .get("SupplyDetail", {})
        .get("Price", [])
    )

    # リストで包むことで、受け取った値の形を辞書型の場合でもリストの場合でも同じにして後続処理を簡易化
    if isinstance(prices, dict):
        prices = [prices]

    if not prices:
        return None

    return _normalize_openbd_price(prices[0].get("PriceAmount"))


def _normalize_openbd_price(value: Any) -> int | None:
    digits = re.sub(r"\D", "", str(value or ""))
    if not digits:
        return None

    # アプリ内データの型をDBモデルに合わせるためのint()
    return int(digits)


def book_to_lookup_data(book: Book) -> dict[str, Any]:
    """Map an existing Book into the same shape as openBD lookup data."""
    return {
        "isbn": book.isbn,
        "title": book.title,
        "author": book.author or "",
        "publisher": book.publisher or "",
        "published_date": book.published_date,
        "cover_image_url": book.cover_image_url or "",
        "price": book.price,
        "genre_code": book.genre_id or "",
    }


def lookup_book_info_by_isbn(isbn: str) -> dict[str, Any] | None:
    """Look up book registration data by ISBN, preferring existing DB records."""
    normalized_isbn = normalize_isbn(isbn)

    # .first()によって見つからなかった場合にNoneを返すようになる（例外処理が不要）
    book = Book.objects.filter(isbn=normalized_isbn).first()
    if book:
        return book_to_lookup_data(book)

    openbd_data = fetch_openbd_book_data(normalized_isbn)
    if openbd_data is None:
        return None

    return map_openbd_book_data(openbd_data, normalized_isbn)
