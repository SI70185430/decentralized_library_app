from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView

from lending.serializers import (
    BorrowBookSerializer,
    CurrentLendingListResponseSerializer,
    LendingActionResponseSerializer,
    LendingHistoryListResponseSerializer,
    ReservationActionResponseSerializer,
    ReservationCreateSerializer,
    ReservationListResponseSerializer,
)
from lending.services.book_actions import (
    ActionConflictError,
    BookNotFoundError,
    LendingNotFoundError,
    borrow_book,
    extend_lending,
    list_current_lendings,
    list_lending_history,
    return_lending,
)
from lending.services.reservation_actions import (
    ReservationNotFoundError,
    cancel_reservation,
    convert_reservation_to_lending,
    create_reservation,
    list_current_reservations,
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
        "scheduled_date": serializers.ListField(
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
    @extend_schema(
        request=None,
        responses={200: CurrentLendingListResponseSerializer(many=True)},
    )
    def get(self, request):
        lendings = list_current_lendings(user=request.user)
        response_serializer = CurrentLendingListResponseSerializer(lendings, many=True)
        return Response(response_serializer.data, status=status.HTTP_200_OK)


class MyLendingHistoryListView(APIView):
    @extend_schema(
        request=None,
        responses={200: LendingHistoryListResponseSerializer(many=True)},
    )
    def get(self, request):
        lendings = list_lending_history(user=request.user)
        response_serializer = LendingHistoryListResponseSerializer(lendings, many=True)
        return Response(response_serializer.data, status=status.HTTP_200_OK)


class ReservationCreateView(APIView):
    @extend_schema(
        request=ReservationCreateSerializer,
        responses={
            201: ReservationActionResponseSerializer,
            400: ValidationErrorResponseSerializer,
            403: ForbiddenResponseSerializer,
            404: NotFoundResponseSerializer,
            409: ConflictResponseSerializer,
        },
    )
    def post(self, request):
        serializer = ReservationCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            reservation = create_reservation(
                user=request.user,
                book_id=serializer.validated_data["book_id"],
                scheduled_date=serializer.validated_data["scheduled_date"],
            )
        except BookNotFoundError as error:
            return not_found_response(error)
        except ActionConflictError as error:
            return conflict_response(error)

        response_serializer = ReservationActionResponseSerializer(reservation)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class ReservationDetailView(APIView):
    @extend_schema(responses={501: NotImplementedResponseSerializer})
    def get(self, request, reservation_id):
        return not_implemented_response()


class ReservationCancelView(APIView):
    @extend_schema(
        request=None,
        responses={
            204: None,
            403: ForbiddenResponseSerializer,
            404: NotFoundResponseSerializer,
        },
    )
    def post(self, request, reservation_id):
        try:
            cancel_reservation(user=request.user, reservation_id=reservation_id)
        except ReservationNotFoundError as error:
            return not_found_response(error)

        return Response(status=status.HTTP_204_NO_CONTENT)


class ReservationConvertToLendingView(APIView):
    @extend_schema(
        request=None,
        responses={
            200: LendingActionResponseSerializer,
            403: ForbiddenResponseSerializer,
            404: NotFoundResponseSerializer,
            409: ConflictResponseSerializer,
        },
    )
    def post(self, request, reservation_id):
        try:
            lending = convert_reservation_to_lending(user=request.user, reservation_id=reservation_id)
        except ReservationNotFoundError as error:
            return not_found_response(error)
        except ActionConflictError as error:
            return conflict_response(error)

        response_serializer = LendingActionResponseSerializer(lending)
        return Response(response_serializer.data, status=status.HTTP_200_OK)


class MyCurrentReservationListView(APIView):
    @extend_schema(
        request=None,
        responses={200: ReservationListResponseSerializer(many=True)},
    )
    def get(self, request):
        reservations = list_current_reservations(user=request.user)
        response_serializer = ReservationListResponseSerializer(reservations, many=True)
        return Response(response_serializer.data, status=status.HTTP_200_OK)
