import re

from django.core.exceptions import ValidationError

ISBN_ERROR_MESSAGE = "10桁または13桁で正当なISBNを入力してください"


def normalize_isbn(value: str) -> str:
    """ユーザーが入力したISBNをISBN-13の数字列へ正規化する。"""
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
    """正規化済みISBN-10のチェックディジットが有効かを返す。"""
    total = 0
    for index, char in enumerate(value):
        digit = 10 if char == "X" else int(char)
        total += digit * (10 - index)

    return total % 11 == 0


def is_valid_isbn13(value: str) -> bool:
    """正規化済みISBN-13のチェックディジットが有効かを返す。"""
    return calculate_isbn13_check_digit(value[:12]) == int(value[12])


def convert_isbn10_to_isbn13(value: str) -> str:
    """正規化済みISBN-10をISBN-13へ変換する。"""
    prefix_body = f"978{value[:9]}"
    check_digit = calculate_isbn13_check_digit(prefix_body)
    return f"{prefix_body}{check_digit}"


def calculate_isbn13_check_digit(value: str) -> int:
    """先頭12桁からISBN-13のチェックディジットを計算する。"""
    total = sum(int(digit) * (1 if index % 2 == 0 else 3) for index, digit in enumerate(value))
    return (10 - total % 10) % 10
