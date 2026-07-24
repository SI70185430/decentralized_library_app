from rest_framework import serializers

from config.api_errors import ApiErrorCode

_VALIDATION_FIELD_CODES = (
    ApiErrorCode.INVALID_CREDENTIALS.value,
    ApiErrorCode.ISBN_INVALID.value,
    ApiErrorCode.GENRE_NOT_FOUND.value,
    ApiErrorCode.RESERVATION_DATE_MUST_BE_FUTURE.value,
    ApiErrorCode.REQUIRED.value,
    ApiErrorCode.BLANK.value,
    ApiErrorCode.INVALID.value,
)
_NON_VALIDATION_CODES = tuple(
    code.value
    for code in ApiErrorCode
    if code.value not in {*_VALIDATION_FIELD_CODES, ApiErrorCode.VALIDATION_ERROR.value}
)


class ApiErrorResponseSerializer(serializers.Serializer):
    """Common non-validation error envelope."""

    code = serializers.ChoiceField(
        choices=_NON_VALIDATION_CODES,
        help_text="機械可読な API error code。表示文言は Frontend が決定する。",
    )


class ValidationErrorResponseSerializer(serializers.Serializer):
    """Common validation error envelope."""

    code = serializers.ChoiceField(
        choices=[ApiErrorCode.VALIDATION_ERROR.value],
        help_text="Validation error の固定 code。",
    )
    field_errors = serializers.DictField(
        child=serializers.ListField(
            child=serializers.ChoiceField(choices=_VALIDATION_FIELD_CODES),
        ),
        help_text="Field ごとの機械可読な validation error code 配列。",
    )


# Explicit alias for callers that prefer the API-prefixed name.
ApiValidationErrorResponseSerializer = ValidationErrorResponseSerializer
