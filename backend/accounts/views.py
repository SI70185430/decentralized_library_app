import logging

from django.contrib.auth import login, logout
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.serializers import LoginSerializer, UserSerializer
from config.api_error_serializers import (
    ApiErrorResponseSerializer,
    ValidationErrorResponseSerializer,
)
from lending.services.reservation_actions import release_expired_reservations

logger = logging.getLogger(__name__)

# SwaggerUIでのレスポンス表示内容のためのシリアライザー
OkResponseSerializer = inline_serializer(
    name="OkResponse",
    fields={"detail": serializers.CharField()},
)
UserResponseSerializer = inline_serializer(
    name="UserResponse",
    fields={"user": UserSerializer()},
)


@method_decorator(ensure_csrf_cookie, name="dispatch")
class CsrfTokenView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(responses={200: OkResponseSerializer})
    def get(self, _request):
        return Response({"detail": "OK"}, status=status.HTTP_200_OK)


@method_decorator(csrf_protect, name="dispatch")
class LoginView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=LoginSerializer,
        responses={
            200: UserResponseSerializer,
            400: ValidationErrorResponseSerializer,
        },
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.user
        login(request, user)
        try:
            release_expired_reservations()
        except Exception:
            logger.exception("ログイン後の期限切れ予約解放に失敗しました")
        return Response({"user": UserSerializer(user).data}, status=status.HTTP_200_OK)


@method_decorator(csrf_protect, name="dispatch")
class LogoutView(APIView):
    @extend_schema(
        request=None,
        responses={200: OkResponseSerializer, 403: ApiErrorResponseSerializer},
    )
    def post(self, request):
        logout(request)
        return Response({"detail": "OK"}, status=status.HTTP_200_OK)


class MeView(APIView):
    @extend_schema(
        responses={200: UserResponseSerializer, 403: ApiErrorResponseSerializer},
    )
    def get(self, request):
        return Response({"user": UserSerializer(request.user).data}, status=status.HTTP_200_OK)
