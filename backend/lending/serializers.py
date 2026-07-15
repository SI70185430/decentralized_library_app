from datetime import timedelta

from django.utils import timezone
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from lending.services.book_actions import DEFAULT_LENDING_DAYS


class BorrowBookSerializer(serializers.Serializer):
    book_id = serializers.UUIDField()


class ReservationCreateSerializer(serializers.Serializer):
    book_id = serializers.UUIDField()
    scheduled_date = serializers.DateField()

    def validate_scheduled_date(self, value):
        if value <= timezone.localdate():
            raise serializers.ValidationError("予約日は明日以降の日付を指定してください")
        return value


class BookSummarySerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    title = serializers.CharField(read_only=True)
    cover_image_url = serializers.URLField(read_only=True, allow_null=True)


class LendingCreateResponseSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)


class LendingActionResponseSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    book_copy_id = serializers.UUIDField(read_only=True)
    book_id = serializers.UUIDField(read_only=True, source="book_copy.book_id")
    borrowed_date = serializers.DateField(read_only=True)
    due_date = serializers.DateField(read_only=True)
    returned_date = serializers.DateField(read_only=True, allow_null=True)
    extension_count = serializers.IntegerField(read_only=True)


class LendingDetailResponseSerializer(serializers.Serializer):
    book_id = serializers.UUIDField(source="book_copy.book_id", read_only=True)
    book_title = serializers.CharField(source="book_copy.book.title", read_only=True)
    cover_image_url = serializers.URLField(
        source="book_copy.book.cover_image_url",
        read_only=True,
        allow_null=True,
    )
    book_copy_location = serializers.CharField(source="book_copy.location", read_only=True)
    borrowed_date = serializers.DateField(read_only=True)
    due_date = serializers.DateField(read_only=True)


class BaseLendingListResponseSerializer(serializers.Serializer):
    book = BookSummarySerializer(source="book_copy.book", read_only=True)


class CurrentLendingListResponseSerializer(BaseLendingListResponseSerializer):
    due_date = serializers.DateField(read_only=True)
    book_copy_location = serializers.CharField(source="book_copy.location", read_only=True)


class LendingHistoryListResponseSerializer(BaseLendingListResponseSerializer):
    lending_id = serializers.UUIDField(source="id", read_only=True)
    borrowed_date = serializers.DateField(read_only=True)
    returned_date = serializers.DateField(read_only=True, allow_null=True)


class ReservationCreateResponseSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)


class ReservationActionResponseSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    book_copy_id = serializers.UUIDField(read_only=True)
    book_id = serializers.UUIDField(read_only=True, source="book_copy.book_id")
    scheduled_date = serializers.DateField(read_only=True)
    expires_date = serializers.DateField(read_only=True)


class ReservationDetailResponseSerializer(serializers.Serializer):
    book_title = serializers.CharField(source="book_copy.book.title", read_only=True)
    scheduled_date = serializers.DateField(read_only=True)
    expires_date = serializers.DateField(read_only=True)
    loan_period_start = serializers.DateField(source="scheduled_date", read_only=True)
    loan_period_end = serializers.SerializerMethodField()

    @extend_schema_field(serializers.DateField)
    def get_loan_period_end(self, obj):
        return obj.scheduled_date + timedelta(days=DEFAULT_LENDING_DAYS - 1)


class ReservationListResponseSerializer(serializers.Serializer):
    book = BookSummarySerializer(source="book_copy.book", read_only=True)
    scheduled_date = serializers.DateField(read_only=True)
    expires_date = serializers.DateField(read_only=True)
