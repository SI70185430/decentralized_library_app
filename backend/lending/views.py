from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView


def success_response():
    return Response(
        {"detail": "OK"},
        status=status.HTTP_200_OK,
    )


class LendingCreateView(APIView):
    def post(self, request):
        return success_response()


class LendingDetailView(APIView):
    def get(self, request, lending_id):
        return success_response()


class LendingExtendView(APIView):
    def post(self, request, lending_id):
        return success_response()


class LendingReturnView(APIView):
    def post(self, request, lending_id):
        return success_response()


class MyCurrentLendingListView(APIView):
    def get(self, request):
        return success_response()


class MyLendingHistoryListView(APIView):
    def get(self, request):
        return success_response()


class ReservationCreateView(APIView):
    def post(self, request):
        return success_response()


class ReservationDetailView(APIView):
    def get(self, request, reservation_id):
        return success_response()


class ReservationCancelView(APIView):
    def post(self, request, reservation_id):
        return success_response()


class ReservationConvertToLendingView(APIView):
    def post(self, request, reservation_id):
        return success_response()


class MyCurrentReservationListView(APIView):
    def get(self, request):
        return success_response()
