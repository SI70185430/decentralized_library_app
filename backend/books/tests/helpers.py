import json
from datetime import date
from unittest.mock import Mock

from django.contrib.auth import get_user_model

from books.models import Book, BookCopy, Genre

VALID_ISBN = "9784003101018"
VALID_ISBN_WITH_HYPHENS = "978-4-00-310101-8"
INVALID_ISBN = "4003101014"
DEFAULT_TITLE = "吾輩は猫である"
DEFAULT_AUTHOR = "夏目漱石"
DEFAULT_PUBLISHER = "岩波書店"
DEFAULT_LOCATION = "1F-A-01"
DEFAULT_COVER_IMAGE_URL = "https://example.com/cover.jpg"
DEFAULT_PUBLISHED_DATE = date(1990, 4, 1)
DEFAULT_PURCHASE_DATE = date(2026, 6, 7)
DEFAULT_PRICE = 1200
DEFAULT_GENRE_CODE = "55"
DEFAULT_GENRE_NAME = "電気通信"
DEFAULT_PASSWORD = "password123"


def create_genre(code=DEFAULT_GENRE_CODE, name=DEFAULT_GENRE_NAME) -> Genre:
    return Genre.objects.create(c_code_genre=code, name=name)


def create_book(
    *,
    genre=None,
    isbn=VALID_ISBN,
    title=DEFAULT_TITLE,
    author=DEFAULT_AUTHOR,
    publisher=None,
    published_date=None,
    price=None,
    cover_image_url="",
    description=None,
    **overrides,
) -> Book:
    data = {
        "isbn": isbn,
        "title": title,
        "author": author,
        "publisher": publisher,
        "published_date": published_date,
        "price": price,
        "cover_image_url": cover_image_url,
        "description": description,
    }
    if genre is not None:
        data["genre"] = genre
    data.update(overrides)
    return Book.objects.create(**data)


def create_book_copy(
    *,
    book=None,
    location=DEFAULT_LOCATION,
    purchase_date=DEFAULT_PURCHASE_DATE,
    **overrides,
) -> BookCopy:
    if book is None:
        book = create_book()

    data = {
        "book": book,
        "location": location,
        "purchase_date": purchase_date,
    }
    data.update(overrides)
    return BookCopy.objects.create(**data)


def create_staff_user(
    *,
    username="book-admin",
    employee_id=700000,
    password=DEFAULT_PASSWORD,
    **overrides,
):
    User = get_user_model()
    data = {
        "username": username,
        "employee_id": employee_id,
        "password": password,
        "is_staff": True,
    }
    data.update(overrides)
    return User.objects.create_user(**data)


def book_register_form_data(**overrides) -> dict:
    data = {
        "isbn": VALID_ISBN_WITH_HYPHENS,
        "title": DEFAULT_TITLE,
        "author": DEFAULT_AUTHOR,
        "publisher": DEFAULT_PUBLISHER,
        "published_date": "1990-04-01",
        "cover_image_url": DEFAULT_COVER_IMAGE_URL,
        "price": str(DEFAULT_PRICE),
        "genre_code": "",
        "purchase_date": "2026-06-07",
        "location": DEFAULT_LOCATION,
        "copy_count": "1",
    }
    data.update(overrides)
    return data


def book_registration_cleaned_data(**overrides) -> dict:
    data = {
        "isbn": VALID_ISBN,
        "title": "新規書籍",
        "author": "新規著者",
        "publisher": "新規出版社",
        "published_date": DEFAULT_PUBLISHED_DATE,
        "price": DEFAULT_PRICE,
        "cover_image_url": "https://example.com/new.jpg",
        "genre_code": DEFAULT_GENRE_CODE,
        "purchase_date": DEFAULT_PURCHASE_DATE,
        "location": DEFAULT_LOCATION,
        "copy_count": 1,
    }
    data.update(overrides)
    return data


def openbd_summary_payload(**overrides) -> dict:
    data = {
        "isbn": VALID_ISBN,
        "title": DEFAULT_TITLE,
        "author": DEFAULT_AUTHOR,
        "publisher": DEFAULT_PUBLISHER,
        "pubdate": "199004",
        "cover": DEFAULT_COVER_IMAGE_URL,
    }
    data.update(overrides)
    return data


def openbd_book_payload(*, summary=None, onix=None, **summary_overrides) -> dict:
    if summary is None:
        summary = openbd_summary_payload(**summary_overrides)
    if onix is None:
        onix = {
            "ProductSupply": {
                "SupplyDetail": {
                    "Price": [{"PriceAmount": "1,200円"}],
                }
            },
        }
    return {"summary": summary, "onix": onix}


def make_urlopen_json_response(payload) -> Mock:
    response = Mock()
    response.__enter__ = Mock(return_value=response)
    response.__exit__ = Mock(return_value=None)
    response.read.return_value = json.dumps(payload).encode()
    return response
