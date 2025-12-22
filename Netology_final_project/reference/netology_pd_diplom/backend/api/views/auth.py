"""
Views для регистрации и аутентификации пользователей.
"""

from backend.api.serializers.user import UserSerializer
from backend.models import ConfirmEmailToken
from backend.tasks.celery_tasks import send_confirmation_email_task
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.http import JsonResponse
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


class RegisterAccount(APIView):
    """
    Регистрация пользователей.
    """

    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        """
        Регистрация пользователя.
        """
        required_fields = {
            "first_name",
            "last_name",
            "email",
            "password",
            "company",
            "position",
        }
        if not required_fields.issubset(request.data):
            return JsonResponse(
                {"Status": False, "Errors": "Не указаны все необходимые аргументы"}
            )

        try:
            validate_password(request.data["password"])
        except Exception as password_error:
            return JsonResponse(
                {"Status": False, "Errors": {"password": list(password_error)}}
            )

        user_serializer = UserSerializer(data=request.data)
        if not user_serializer.is_valid():
            return JsonResponse({"Status": False, "Errors": user_serializer.errors})

        user = user_serializer.save()
        user.set_password(request.data["password"])
        user.is_active = False
        user.save()

        token = ConfirmEmailToken.objects.create(user=user)
        send_confirmation_email_task.delay(user.id)

        return JsonResponse(
            {
                "Status": True,
                "Message": f"Пользователь {user.first_name} {user.last_name} создан. Проверьте email для подтверждения регистрации.",
            }
        )


class ConfirmAccount(APIView):
    """
    Подтверждение email.
    """

    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        """
        Отправка токена.
        """
        required_fields = {"email", "token"}
        if not required_fields.issubset(request.data):
            return JsonResponse(
                {"Status": False, "Errors": "Не указаны все необходимые аргументы"}
            )

        try:
            token = ConfirmEmailToken.objects.get(
                user__email=request.data["email"],
                key=request.data["token"],
            )
        except ConfirmEmailToken.DoesNotExist:
            return JsonResponse({"Status": False, "Error": "Неверный токен или email"})

        user = token.user
        user.is_active = True
        user.save()
        token.delete()

        return JsonResponse(
            {
                "Status": True,
                "Message": "Email успешно подтверждён. Теперь вы можете войти в систему.",
            }
        )


class LoginAccount(APIView):
    """
    Авторизация пользователей.
    """

    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        """
        Вход в систему.
        """
        required_fields = {"email", "password"}
        if not required_fields.issubset(request.data):
            return JsonResponse(
                {"Status": False, "Errors": "Не указаны все необходимые аргументы"}
            )

        user = authenticate(
            request, username=request.data["email"], password=request.data["password"]
        )

        if user and user.is_active:
            token, _ = Token.objects.get_or_create(user=user)
            return JsonResponse(
                {
                    "Status": True,
                    "Token": token.key,
                    "Message": "Запишите ваш токен для работы с API",
                }
            )

        return JsonResponse({"Status": False, "Errors": "Не удалось авторизовать"})


class AccountDetails(APIView):
    """
    Управление данными аккаунта.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """
        Проверка прав доступа для GET запросов.
        """

        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        """
        Проверка прав доступа для POST запросов.
        """

        if "password" in request.data:
            try:
                validate_password(request.data["password"])
            except Exception as password_error:
                return JsonResponse(
                    {"Status": False, "Errors": {"password": list(password_error)}}
                )
            request.user.set_password(request.data["password"])

        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse({"Status": True})

        return JsonResponse({"Status": False, "Errors": serializer.errors})
