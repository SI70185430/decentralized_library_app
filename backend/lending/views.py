from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from lending.serializers import BorrowBookSerializer, LendingActionResponseSerializer
from lending.services.book_actions import (
    ActionConflictError,
    borrow_book,
    extend_lending,
    return_lending,
)

OkResponseSerializer = inline_serializer(
    name="LendingOkResponse",
    fields={"detail": serializers.CharField()},
)
ErrorResponseSerializer = inline_serializer(
    name="LendingErrorResponse",
    fields={"detail": serializers.CharField()},
)


def success_response():
    return Response(
        {"detail": "OK"},
        status=status.HTTP_200_OK,
    )


def conflict_response(error: ActionConflictError) -> Response:
    return Response(
        {"detail": str(error)},
        status=status.HTTP_409_CONFLICT,
    )


class LendingCreateView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=BorrowBookSerializer,
        responses={
            201: LendingActionResponseSerializer,
            409: ErrorResponseSerializer,
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
        except ActionConflictError as error:
            return conflict_response(error)

        response_serializer = LendingActionResponseSerializer(lending)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class LendingDetailView(APIView):
    @extend_schema(responses={200: OkResponseSerializer})
    def get(self, request, lending_id):
        return success_response()


class LendingExtendView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=None,
        responses={
            200: LendingActionResponseSerializer,
            409: ErrorResponseSerializer,
        },
    )
    def post(self, request, lending_id):
        try:
            lending = extend_lending(user=request.user, lending_id=lending_id)
        except ActionConflictError as error:
            return conflict_response(error)

        response_serializer = LendingActionResponseSerializer(lending)
        return Response(response_serializer.data, status=status.HTTP_200_OK)


class LendingReturnView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=None,
        responses={
            200: LendingActionResponseSerializer,
            409: ErrorResponseSerializer,
        },
    )
    def post(self, request, lending_id):
        try:
            lending = return_lending(user=request.user, lending_id=lending_id)
        except ActionConflictError as error:
            return conflict_response(error)

        response_serializer = LendingActionResponseSerializer(lending)
        return Response(response_serializer.data, status=status.HTTP_200_OK)


class MyCurrentLendingListView(APIView):
    @extend_schema(responses={200: OkResponseSerializer})
    def get(self, request):
        return success_response()


class MyLendingHistoryListView(APIView):
    @extend_schema(responses={200: OkResponseSerializer})
    def get(self, request):
        return success_response()


class ReservationCreateView(APIView):
    @extend_schema(request=None, responses={200: OkResponseSerializer})
    def post(self, request):
        return success_response()


class ReservationDetailView(APIView):
    @extend_schema(responses={200: OkResponseSerializer})
    def get(self, request, reservation_id):
        return success_response()


class ReservationCancelView(APIView):
    @extend_schema(request=None, responses={200: OkResponseSerializer})
    def post(self, request, reservation_id):
        return success_response()


class ReservationConvertToLendingView(APIView):
    @extend_schema(request=None, responses={200: OkResponseSerializer})
    def post(self, request, reservation_id):
        return success_response()


class MyCurrentReservationListView(APIView):
    @extend_schema(responses={200: OkResponseSerializer})
    def get(self, request):
        return success_response()
