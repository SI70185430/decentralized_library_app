from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from config.api_error_serializers import (
    ApiErrorResponseSerializer,
    ValidationErrorResponseSerializer,
)
from lending.serializers import (
    BorrowBookSerializer,
    CurrentLendingListResponseSerializer,
    LendingActionResponseSerializer,
    LendingCompletionResponseSerializer,
    LendingCreateResponseSerializer,
    LendingHistoryListResponseSerializer,
    LendingReturnPreviewResponseSerializer,
    ReservationCreateResponseSerializer,
    ReservationCreateSerializer,
    ReservationDetailResponseSerializer,
    ReservationListResponseSerializer,
)
from lending.services.book_actions import (
    borrow_book,
    extend_lending,
    get_lending_detail,
    list_current_lendings,
    list_lending_history,
    return_lending,
)
from lending.services.reservation_actions import (
    cancel_reservation,
    convert_reservation_to_lending,
    create_reservation,
    get_reservation_detail,
    list_current_reservations,
)


class LendingCreateView(APIView):
    @extend_schema(
        request=BorrowBookSerializer,
        responses={
            201: LendingCreateResponseSerializer,
            400: ValidationErrorResponseSerializer,
            403: ApiErrorResponseSerializer,
            404: ApiErrorResponseSerializer,
            409: ApiErrorResponseSerializer,
        },
    )
    def post(self, request):
        serializer = BorrowBookSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        lending = borrow_book(
            user=request.user,
            book_id=serializer.validated_data["book_id"],
        )

        response_serializer = LendingCreateResponseSerializer(lending)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class LendingDetailView(APIView):
    @extend_schema(
        request=None,
        responses={
            200: LendingCompletionResponseSerializer,
            403: ApiErrorResponseSerializer,
            404: ApiErrorResponseSerializer,
        },
    )
    def get(self, request, lending_id):
        lending = get_lending_detail(user=request.user, lending_id=lending_id)
        response_serializer = LendingCompletionResponseSerializer(lending)
        return Response(response_serializer.data, status=status.HTTP_200_OK)


class LendingExtendView(APIView):
    @extend_schema(
        request=None,
        responses={
            200: LendingActionResponseSerializer,
            403: ApiErrorResponseSerializer,
            404: ApiErrorResponseSerializer,
            409: ApiErrorResponseSerializer,
        },
    )
    def post(self, request, lending_id):
        lending = extend_lending(user=request.user, lending_id=lending_id)
        response_serializer = LendingActionResponseSerializer(lending)
        return Response(response_serializer.data, status=status.HTTP_200_OK)


class LendingReturnView(APIView):
    @extend_schema(
        request=None,
        responses={
            200: LendingReturnPreviewResponseSerializer,
            403: ApiErrorResponseSerializer,
            404: ApiErrorResponseSerializer,
        },
    )
    def get(self, request, lending_id):
        lending = get_lending_detail(user=request.user, lending_id=lending_id)
        response_serializer = LendingReturnPreviewResponseSerializer(lending)
        return Response(response_serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=None,
        responses={
            200: LendingActionResponseSerializer,
            403: ApiErrorResponseSerializer,
            404: ApiErrorResponseSerializer,
            409: ApiErrorResponseSerializer,
        },
    )
    def post(self, request, lending_id):
        lending = return_lending(user=request.user, lending_id=lending_id)
        response_serializer = LendingActionResponseSerializer(lending)
        return Response(response_serializer.data, status=status.HTTP_200_OK)


class MyCurrentLendingListView(APIView):
    @extend_schema(
        request=None,
        responses={
            200: CurrentLendingListResponseSerializer(many=True),
            403: ApiErrorResponseSerializer,
        },
    )
    def get(self, request):
        lendings = list_current_lendings(user=request.user)
        response_serializer = CurrentLendingListResponseSerializer(lendings, many=True)
        return Response(response_serializer.data, status=status.HTTP_200_OK)


class MyLendingHistoryListView(APIView):
    @extend_schema(
        request=None,
        responses={
            200: LendingHistoryListResponseSerializer(many=True),
            403: ApiErrorResponseSerializer,
        },
    )
    def get(self, request):
        lendings = list_lending_history(user=request.user)
        response_serializer = LendingHistoryListResponseSerializer(lendings, many=True)
        return Response(response_serializer.data, status=status.HTTP_200_OK)


class ReservationCreateView(APIView):
    @extend_schema(
        request=ReservationCreateSerializer,
        responses={
            201: ReservationCreateResponseSerializer,
            400: ValidationErrorResponseSerializer,
            403: ApiErrorResponseSerializer,
            404: ApiErrorResponseSerializer,
            409: ApiErrorResponseSerializer,
        },
    )
    def post(self, request):
        serializer = ReservationCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        reservation = create_reservation(
            user=request.user,
            book_id=serializer.validated_data["book_id"],
            scheduled_date=serializer.validated_data["scheduled_date"],
        )

        response_serializer = ReservationCreateResponseSerializer(reservation)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class ReservationDetailView(APIView):
    @extend_schema(
        request=None,
        responses={
            200: ReservationDetailResponseSerializer,
            403: ApiErrorResponseSerializer,
            404: ApiErrorResponseSerializer,
        },
    )
    def get(self, request, reservation_id):
        reservation = get_reservation_detail(user=request.user, reservation_id=reservation_id)
        response_serializer = ReservationDetailResponseSerializer(reservation)
        return Response(response_serializer.data, status=status.HTTP_200_OK)


class ReservationCancelView(APIView):
    @extend_schema(
        request=None,
        responses={
            204: None,
            403: ApiErrorResponseSerializer,
            404: ApiErrorResponseSerializer,
        },
    )
    def post(self, request, reservation_id):
        cancel_reservation(user=request.user, reservation_id=reservation_id)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ReservationConvertToLendingView(APIView):
    @extend_schema(
        request=None,
        responses={
            200: LendingActionResponseSerializer,
            403: ApiErrorResponseSerializer,
            404: ApiErrorResponseSerializer,
            409: ApiErrorResponseSerializer,
        },
    )
    def post(self, request, reservation_id):
        lending = convert_reservation_to_lending(user=request.user, reservation_id=reservation_id)
        response_serializer = LendingActionResponseSerializer(lending)
        return Response(response_serializer.data, status=status.HTTP_200_OK)


class MyCurrentReservationListView(APIView):
    @extend_schema(
        request=None,
        responses={
            200: ReservationListResponseSerializer(many=True),
            403: ApiErrorResponseSerializer,
        },
    )
    def get(self, request):
        reservations = list_current_reservations(user=request.user)
        response_serializer = ReservationListResponseSerializer(reservations, many=True)
        return Response(response_serializer.data, status=status.HTTP_200_OK)
