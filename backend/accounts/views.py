from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView


def success_response():
    return Response(
        {"detail": "OK"},
        status=status.HTTP_200_OK,
    )


class CsrfTokenView(APIView):
    def get(self, request):
        return success_response()


class LoginView(APIView):
    def post(self, request):
        return success_response()


class LogoutView(APIView):
    def post(self, request):
        return success_response()


class MeView(APIView):
    def get(self, request):
        return success_response()
