from django.core.exceptions import PermissionDenied as DjangoPermissionDenied
from django.http import Http404
from rest_framework import exceptions
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler
from rest_framework.views import set_rollback

from config.api_errors import ApiErrorCode, DomainError, normalize_validation_code


def _validation_field_errors(error: exceptions.ValidationError) -> dict[str, list[str]]:
    """Return only public validation codes, even for an unexpected DRF shape."""
    try:
        codes = error.get_codes()
    except Exception:
        return {"non_field_errors": [ApiErrorCode.INVALID.value]}

    if isinstance(codes, dict):
        normalized: dict[str, list[str]] = {}
        for field, field_codes in codes.items():
            field_name = field if isinstance(field, str) else "non_field_errors"
            normalized.setdefault(field_name, []).extend(_normalize_code_values(field_codes))
        return normalized or {"non_field_errors": [ApiErrorCode.INVALID.value]}

    return {"non_field_errors": _normalize_code_values(codes)}


def _normalize_code_values(value: object) -> list[str]:
    if isinstance(value, (list, tuple)):
        normalized: list[str] = []
        for item in value:
            if isinstance(item, (dict, list, tuple)):
                normalized.append(ApiErrorCode.INVALID.value)
            else:
                normalized.append(normalize_validation_code(item))
        return normalized or [ApiErrorCode.INVALID.value]

    return [normalize_validation_code(value)]


def _with_data(response: Response, data: dict[str, object]) -> Response:
    response.data = data
    return response


def api_exception_handler(exc: Exception, context: dict) -> Response | None:
    """Map contract-targeted exceptions without exposing their messages."""
    if isinstance(exc, DomainError):
        set_rollback()
        return Response({"code": exc.code.value}, status=exc.status_code)

    response = drf_exception_handler(exc, context)
    if response is None:
        # Keep unexpected exceptions on Django's normal 500/logging path.
        return None

    if isinstance(exc, exceptions.ValidationError):
        return _with_data(
            response,
            {
                "code": ApiErrorCode.VALIDATION_ERROR.value,
                "field_errors": _validation_field_errors(exc),
            },
        )

    if isinstance(exc, (exceptions.NotAuthenticated, exceptions.AuthenticationFailed)):
        return _with_data(response, {"code": ApiErrorCode.AUTHENTICATION_REQUIRED.value})

    if isinstance(exc, (exceptions.PermissionDenied, DjangoPermissionDenied)):
        return _with_data(response, {"code": ApiErrorCode.FORBIDDEN.value})

    if isinstance(exc, (exceptions.NotFound, Http404)):
        return _with_data(response, {"code": ApiErrorCode.NOT_FOUND.value})

    # ParseError, method/content-negotiation errors, throttling, and other DRF
    # framework errors intentionally retain DRF's standard response.
    return response
