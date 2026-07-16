from enum import StrEnum
from typing import Final

from rest_framework import status


class ApiErrorCode(StrEnum):
    """Codes that are safe to expose at the API boundary."""

    INVALID_CREDENTIALS = "INVALID_CREDENTIALS"
    ISBN_INVALID = "ISBN_INVALID"
    GENRE_NOT_FOUND = "GENRE_NOT_FOUND"
    RESERVATION_DATE_MUST_BE_FUTURE = "RESERVATION_DATE_MUST_BE_FUTURE"

    BOOK_NOT_FOUND = "BOOK_NOT_FOUND"
    LENDING_NOT_FOUND = "LENDING_NOT_FOUND"
    RESERVATION_NOT_FOUND = "RESERVATION_NOT_FOUND"

    BORROWING_LIMIT_REACHED = "BORROWING_LIMIT_REACHED"
    ALREADY_BORROWING_BOOK = "ALREADY_BORROWING_BOOK"
    ALREADY_RESERVING_BOOK = "ALREADY_RESERVING_BOOK"
    NO_AVAILABLE_BOOK_COPY = "NO_AVAILABLE_BOOK_COPY"
    BOOK_COPY_ALREADY_RESERVED = "BOOK_COPY_ALREADY_RESERVED"
    LENDING_EXTENSION_LIMIT_REACHED = "LENDING_EXTENSION_LIMIT_REACHED"
    LENDING_ALREADY_RETURNED = "LENDING_ALREADY_RETURNED"
    BOOK_COPY_NOT_ON_LOAN = "BOOK_COPY_NOT_ON_LOAN"
    RESERVATION_NOT_STARTED = "RESERVATION_NOT_STARTED"
    RESERVATION_EXPIRED = "RESERVATION_EXPIRED"
    BOOK_COPY_NOT_RESERVED = "BOOK_COPY_NOT_RESERVED"
    LENDING_STATE_CONFLICT = "LENDING_STATE_CONFLICT"

    REQUIRED = "REQUIRED"
    BLANK = "BLANK"
    INVALID = "INVALID"
    AUTHENTICATION_REQUIRED = "AUTHENTICATION_REQUIRED"
    FORBIDDEN = "FORBIDDEN"
    NOT_FOUND = "NOT_FOUND"
    VALIDATION_ERROR = "VALIDATION_ERROR"


API_ERROR_STATUS: Final[dict[ApiErrorCode, int]] = {
    ApiErrorCode.INVALID_CREDENTIALS: status.HTTP_400_BAD_REQUEST,
    ApiErrorCode.ISBN_INVALID: status.HTTP_400_BAD_REQUEST,
    ApiErrorCode.GENRE_NOT_FOUND: status.HTTP_400_BAD_REQUEST,
    ApiErrorCode.RESERVATION_DATE_MUST_BE_FUTURE: status.HTTP_400_BAD_REQUEST,
    ApiErrorCode.BOOK_NOT_FOUND: status.HTTP_404_NOT_FOUND,
    ApiErrorCode.LENDING_NOT_FOUND: status.HTTP_404_NOT_FOUND,
    ApiErrorCode.RESERVATION_NOT_FOUND: status.HTTP_404_NOT_FOUND,
    ApiErrorCode.BORROWING_LIMIT_REACHED: status.HTTP_409_CONFLICT,
    ApiErrorCode.ALREADY_BORROWING_BOOK: status.HTTP_409_CONFLICT,
    ApiErrorCode.ALREADY_RESERVING_BOOK: status.HTTP_409_CONFLICT,
    ApiErrorCode.NO_AVAILABLE_BOOK_COPY: status.HTTP_409_CONFLICT,
    ApiErrorCode.BOOK_COPY_ALREADY_RESERVED: status.HTTP_409_CONFLICT,
    ApiErrorCode.LENDING_EXTENSION_LIMIT_REACHED: status.HTTP_409_CONFLICT,
    ApiErrorCode.LENDING_ALREADY_RETURNED: status.HTTP_409_CONFLICT,
    ApiErrorCode.BOOK_COPY_NOT_ON_LOAN: status.HTTP_409_CONFLICT,
    ApiErrorCode.RESERVATION_NOT_STARTED: status.HTTP_409_CONFLICT,
    ApiErrorCode.RESERVATION_EXPIRED: status.HTTP_409_CONFLICT,
    ApiErrorCode.BOOK_COPY_NOT_RESERVED: status.HTTP_409_CONFLICT,
    ApiErrorCode.LENDING_STATE_CONFLICT: status.HTTP_409_CONFLICT,
    ApiErrorCode.REQUIRED: status.HTTP_400_BAD_REQUEST,
    ApiErrorCode.BLANK: status.HTTP_400_BAD_REQUEST,
    ApiErrorCode.INVALID: status.HTTP_400_BAD_REQUEST,
    ApiErrorCode.AUTHENTICATION_REQUIRED: status.HTTP_401_UNAUTHORIZED,
    ApiErrorCode.FORBIDDEN: status.HTTP_403_FORBIDDEN,
    ApiErrorCode.NOT_FOUND: status.HTTP_404_NOT_FOUND,
    ApiErrorCode.VALIDATION_ERROR: status.HTTP_400_BAD_REQUEST,
}

# These are the only codes that a service-layer DomainError may carry. Validation,
# authentication, and framework codes are created at the API boundary instead.
DOMAIN_ERROR_CODES: Final[frozenset[ApiErrorCode]] = frozenset(
    {
        ApiErrorCode.BOOK_NOT_FOUND,
        ApiErrorCode.LENDING_NOT_FOUND,
        ApiErrorCode.RESERVATION_NOT_FOUND,
        ApiErrorCode.BORROWING_LIMIT_REACHED,
        ApiErrorCode.ALREADY_BORROWING_BOOK,
        ApiErrorCode.ALREADY_RESERVING_BOOK,
        ApiErrorCode.NO_AVAILABLE_BOOK_COPY,
        ApiErrorCode.BOOK_COPY_ALREADY_RESERVED,
        ApiErrorCode.LENDING_EXTENSION_LIMIT_REACHED,
        ApiErrorCode.LENDING_ALREADY_RETURNED,
        ApiErrorCode.BOOK_COPY_NOT_ON_LOAN,
        ApiErrorCode.RESERVATION_NOT_STARTED,
        ApiErrorCode.RESERVATION_EXPIRED,
        ApiErrorCode.BOOK_COPY_NOT_RESERVED,
        ApiErrorCode.LENDING_STATE_CONFLICT,
    }
)

VALIDATION_ERROR_CODES: Final[frozenset[str]] = frozenset(
    {
        ApiErrorCode.INVALID_CREDENTIALS.value,
        ApiErrorCode.ISBN_INVALID.value,
        ApiErrorCode.GENRE_NOT_FOUND.value,
        ApiErrorCode.RESERVATION_DATE_MUST_BE_FUTURE.value,
        ApiErrorCode.REQUIRED.value,
        ApiErrorCode.BLANK.value,
        ApiErrorCode.INVALID.value,
    }
)


class DomainError(Exception):
    """An expected business error with no user-facing message."""

    def __init__(self, code: ApiErrorCode):
        if not isinstance(code, ApiErrorCode) or code not in DOMAIN_ERROR_CODES:
            raise ValueError("DomainError requires an allowed domain error code")

        self.code = code
        super().__init__(code.value)

    @property
    def status_code(self) -> int:
        return API_ERROR_STATUS[self.code]


def normalize_validation_code(code: object) -> str:
    """Convert a DRF validation code to the public validation-code catalog."""
    if isinstance(code, ApiErrorCode):
        value = code.value
    elif isinstance(code, str):
        value = code
    else:
        value = ""

    if value in VALIDATION_ERROR_CODES:
        return value

    return {
        "required": ApiErrorCode.REQUIRED.value,
        "blank": ApiErrorCode.BLANK.value,
        "invalid": ApiErrorCode.INVALID.value,
    }.get(value, ApiErrorCode.INVALID.value)
