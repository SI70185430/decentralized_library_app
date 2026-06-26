from django.utils import timezone
from rest_framework import serializers


class BorrowBookSerializer(serializers.Serializer):
    book_id = serializers.UUIDField()


class ReservationCreateSerializer(serializers.Serializer):
    book_id = serializers.UUIDField()
    scheduled_date = serializers.DateField()

    def validate_scheduled_date(self, value):
        if value <= timezone.localdate():
            raise serializers.ValidationError("予約日は明日以降の日付を指定してください")
        return value


class LendingActionResponseSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    book_copy_id = serializers.UUIDField(read_only=True)
    book_id = serializers.UUIDField(read_only=True, source="book_copy.book_id")
    borrowed_date = serializers.DateField(read_only=True)
    due_date = serializers.DateField(read_only=True)
    returned_date = serializers.DateField(read_only=True, allow_null=True)
    extension_count = serializers.IntegerField(read_only=True)


class ReservationActionResponseSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    book_copy_id = serializers.UUIDField(read_only=True)
    book_id = serializers.UUIDField(read_only=True, source="book_copy.book_id")
    scheduled_date = serializers.DateField(read_only=True)
    expires_date = serializers.DateField(read_only=True)
