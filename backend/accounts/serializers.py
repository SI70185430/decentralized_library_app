from django.contrib.auth import get_user_model
from rest_framework import serializers

from config.api_errors import ApiErrorCode

INVALID_LOGIN_MESSAGE = "社員番号またはパスワードが正しくありません"


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ["id", "employee_id", "username"]


class LoginSerializer(serializers.Serializer):
    employee_id = serializers.IntegerField(label="社員ID")
    password = serializers.CharField(label="パスワード", write_only=True, trim_whitespace=False)

    # ログイン認証に成功したユーザーをserializer.userで取得できるように
    @property
    def user(self):
        return self._user

    def validate(self, attrs):
        employee_id = attrs["employee_id"]
        password = attrs["password"]
        User = get_user_model()

        try:
            user = User.objects.get(employee_id=employee_id)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                INVALID_LOGIN_MESSAGE,
                code=ApiErrorCode.INVALID_CREDENTIALS.value,
            ) from None

        if not user.check_password(password) or not user.is_active:
            raise serializers.ValidationError(
                INVALID_LOGIN_MESSAGE,
                code=ApiErrorCode.INVALID_CREDENTIALS.value,
            )

        self._user = user
        return attrs
