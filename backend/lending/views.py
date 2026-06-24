from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView

from lending.serializers import BorrowBookSerializer, LendingActionResponseSerializer
from lending.services.book_actions import (
    ActionConflictError,
    BookNotFoundError,
    LendingNotFoundError,
    borrow_book,
    extend_lending,
    return_lending,
)

NotImplementedResponseSerializer = inline_serializer(
    name="LendingNotImplementedResponse",
    fields={"detail": serializers.CharField()},
)
ConflictResponseSerializer = inline_serializer(
    name="LendingConflictResponse",
    fields={"detail": serializers.CharField()},
)
ForbiddenResponseSerializer = inline_serializer(
    name="LendingForbiddenResponse",
    fields={"detail": serializers.CharField()},
)
NotFoundResponseSerializer = inline_serializer(
    name="LendingNotFoundResponse",
    fields={"detail": serializers.CharField()},
)
ValidationErrorResponseSerializer = inline_serializer(
    name="LendingValidationErrorResponse",
    fields={
        "book_id": serializers.ListField(
            child=serializers.CharField(),
            required=False,
        ),
        "non_field_errors": serializers.ListField(
            child=serializers.CharField(),
            required=False,
        ),
    },
)


def not_implemented_response():
    return Response(
        {"detail": "Not implemented"},
        status=status.HTTP_501_NOT_IMPLEMENTED,
    )


def conflict_response(error: ActionConflictError) -> Response:
    return Response(
        {"detail": str(error)},
        status=status.HTTP_409_CONFLICT,
    )


def not_found_response(error: Exception) -> Response:
    return Response(
        {"detail": str(error)},
        status=status.HTTP_404_NOT_FOUND,
    )


class LendingCreateView(APIView):
    @extend_schema(
        request=BorrowBookSerializer,
        responses={
            201: LendingActionResponseSerializer,
            400: ValidationErrorResponseSerializer,
            403: ForbiddenResponseSerializer,
            404: NotFoundResponseSerializer,
            409: ConflictResponseSerializer,
        },
    )
    def post(self, request):
        serializer = BorrowBookSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            lending = borrow_book(
                user=request.user,
                book_id=serializer.validated_data["book_id"],
            )
        except BookNotFoundError as error:
            return not_found_response(error)
        except ActionConflictError as error:
            return conflict_response(error)

        response_serializer = LendingActionResponseSerializer(lending)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class LendingDetailView(APIView):
    @extend_schema(responses={501: NotImplementedResponseSerializer})
    def get(self, request, lending_id):
        return not_implemented_response()


class LendingExtendView(APIView):
    @extend_schema(
        request=None,
        responses={
            200: LendingActionResponseSerializer,
            403: ForbiddenResponseSerializer,
            404: NotFoundResponseSerializer,
            409: ConflictResponseSerializer,
        },
    )
    def post(self, request, lending_id):
        try:
            lending = extend_lending(user=request.user, lending_id=lending_id)
        except LendingNotFoundError as error:
            return not_found_response(error)
        except ActionConflictError as error:
            return conflict_response(error)

        response_serializer = LendingActionResponseSerializer(lending)
        return Response(response_serializer.data, status=status.HTTP_200_OK)


class LendingReturnView(APIView):
    @extend_schema(
        request=None,
        responses={
            200: LendingActionResponseSerializer,
            403: ForbiddenResponseSerializer,
            404: NotFoundResponseSerializer,
            409: ConflictResponseSerializer,
        },
    )
    def post(self, request, lending_id):
        try:
            lending = return_lending(user=request.user, lending_id=lending_id)
        except LendingNotFoundError as error:
            return not_found_response(error)
        except ActionConflictError as error:
            return conflict_response(error)

        response_serializer = LendingActionResponseSerializer(lending)
        return Response(response_serializer.data, status=status.HTTP_200_OK)


class MyCurrentLendingListView(APIView):
    @extend_schema(responses={501: NotImplementedResponseSerializer})
    def get(self, request):
        return not_implemented_response()


class MyLendingHistoryListView(APIView):
    @extend_schema(responses={501: NotImplementedResponseSerializer})
    def get(self, request):
        return not_implemented_response()


class ReservationCreateView(APIView):
    @extend_schema(request=None, responses={501: NotImplementedResponseSerializer})
    def post(self, request):
        return not_implemented_response()


class ReservationDetailView(APIView):
    @extend_schema(responses={501: NotImplementedResponseSerializer})
    def get(self, request, reservation_id):
        return not_implemented_response()


class ReservationCancelView(APIView):
    @extend_schema(request=None, responses={501: NotImplementedResponseSerializer})
    def post(self, request, reservation_id):
        return not_implemented_response()


class ReservationConvertToLendingView(APIView):
    @extend_schema(request=None, responses={501: NotImplementedResponseSerializer})
    def post(self, request, reservation_id):
        return not_implemented_response()


class MyCurrentReservationListView(APIView):
    @extend_schema(responses={501: NotImplementedResponseSerializer})
    def get(self, request):
        return not_implemented_response()
