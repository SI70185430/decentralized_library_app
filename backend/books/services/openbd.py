import json
import re
import urllib.error
import urllib.parse
import urllib.request
from datetime import date
from typing import Any  # 外部APIを扱う関係でAnyを許容

from books.models import Book
from books.services.isbn import normalize_isbn

OPENBD_ENDPOINT = "https://api.openbd.jp/v1/get"
OPENBD_TIMEOUT_SECONDS = 10


class OpenBdError(Exception):
    """ネットワークまたはレスポンスのエラー用のクラス"""


def parse_openbd_pubdate(value: str | None) -> date | None:
    """openBDのsummary.pubdateをBook.published_date用の日付へ変換する。"""
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
    """正規化済みISBN-13からopenBDの書籍データオブジェクトを取得する。"""
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
    """openBDの書籍データを書籍登録の検索結果データへ変換する。"""
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
    """openBDのONIXデータから価格を抽出する。"""
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
    """既存のBookをopenBD検索結果データと同じ形に変換する。"""
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
    """既存DBレコードを優先してISBNから書籍登録データを検索する。"""
    normalized_isbn = normalize_isbn(isbn)

    # .first()によって見つからなかった場合にNoneを返すようになる（例外処理が不要）
    book = Book.objects.filter(isbn=normalized_isbn).first()
    if book:
        return book_to_lookup_data(book)

    openbd_data = fetch_openbd_book_data(normalized_isbn)
    if openbd_data is None:
        return None

    return map_openbd_book_data(openbd_data, normalized_isbn)
