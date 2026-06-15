import re

from django.core.exceptions import ValidationError

ISBN_ERROR_MESSAGE = "10桁または13桁で正当なISBNを入力してください"


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
