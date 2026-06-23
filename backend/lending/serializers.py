from rest_framework import serializers


class BorrowBookSerializer(serializers.Serializer):
    book_id = serializers.UUIDField()


class LendingActionResponseSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    book_copy_id = serializers.UUIDField(read_only=True)
    book_id = serializers.UUIDField(read_only=True, source="book_copy.book_id")
    borrowed_date = serializers.DateField(read_only=True)
    due_date = serializers.DateField(read_only=True)
    returned_date = serializers.DateField(read_only=True, allow_null=True)
    extension_count = serializers.IntegerField(read_only=True)
