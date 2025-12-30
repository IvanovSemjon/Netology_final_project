from backend.api.serializers.user import UserSerializer
from backend.models import ConfirmEmailToken
from backend.tasks.celery_tasks import send_confirmation_email_task
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from drf_spectacular.utils import extend_schema
from rest_framework import serializers, status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.throttling import ScopedRateThrottle, UserRateThrottle, AnonRateThrottle
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema
from rest_framework.parsers import MultiPartParser, FormParser

User = get_user_model()


class RegisterAccountRequestSerializer(serializers.Serializer):
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    company = serializers.CharField()
    position = serializers.CharField()
    type = serializers.ChoiceField(
        choices=User.USER_TYPE_CHOICES,
        required=False,
        default='buyer'
    )
    avatar = serializers.ImageField(required=False, allow_null=True)


class RegisterAccountResponseSerializer(serializers.Serializer):
    Status = serializers.BooleanField()
    Message = serializers.CharField()


class ErrorResponseSerializer(serializers.Serializer):
    Status = serializers.BooleanField()
    Errors = serializers.DictField()


class ConfirmAccountRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()
    token = serializers.CharField()


class ConfirmAccountResponseSerializer(serializers.Serializer):
    Status = serializers.BooleanField()
    Message = serializers.CharField()


class LoginAccountRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class LoginAccountResponseSerializer(serializers.Serializer):
    Status = serializers.BooleanField()
    Token = serializers.CharField()
    Message = serializers.CharField()


class RegisterAccount(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [UserRateThrottle, AnonRateThrottle, ScopedRateThrottle]
    throttle_scope = 'account'
    parser_classes = [MultiPartParser, FormParser]  # <- вот это важно

    @extend_schema(
        summary="Регистрация пользователя",
        description="Создание нового пользователя и отправка письма для подтверждения email",
        request=RegisterAccountRequestSerializer,
        responses={200: RegisterAccountResponseSerializer, 400: ErrorResponseSerializer},
        tags=["Пользователи"],
    )

    def post(self, request, *args, **kwargs):
        required_fields = {"first_name", "last_name", "email", "password", "company", "position"}
        if not required_fields.issubset(request.data):
            return Response({"Status": False, "Errors": "Не указаны все необходимые аргументы"},
                            status=status.HTTP_400_BAD_REQUEST)

        email = request.data["email"].lower()
        if User.objects.filter(email=email).exists():
            return Response({"Status": False, "Errors": {"email": ["Пользователь с таким email уже существует"]}},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            validate_password(request.data["password"])
        except Exception as password_error:
            return Response({"Status": False, "Errors": {"password": list(password_error)}},
                            status=status.HTTP_400_BAD_REQUEST)

        # сериализатор
        serializer_data = request.data.copy()
        if request.FILES.get("avatar"):
            serializer_data["avatar"] = request.FILES["avatar"]

        user_serializer = UserSerializer(data=serializer_data)
        if not user_serializer.is_valid():
            return Response({"Status": False, "Errors": user_serializer.errors},
                            status=status.HTTP_400_BAD_REQUEST)

        user = user_serializer.save()
        user.set_password(request.data["password"])
        user.is_active = False
        user.save()

        token_obj = ConfirmEmailToken.objects.create(user=user)
        send_confirmation_email_task.delay(user.id)

        return Response({
            "Status": True,
            "Message": f"Пользователь {user.first_name} {user.last_name} создан. Проверьте email для подтверждения регистрации."
        }, status=status.HTTP_200_OK)


class ConfirmAccount(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [UserRateThrottle, AnonRateThrottle]
    throttle_scope = 'account'

    @extend_schema(
        summary="Подтверждение email пользователя",
        description="Подтверждает email по токену, отправленному на почту при регистрации",
        request=ConfirmAccountRequestSerializer,
        responses={200: ConfirmAccountResponseSerializer, 400: ErrorResponseSerializer},
        tags=["Пользователи"],
    )
    def post(self, request, *args, **kwargs):
        required_fields = {"email", "token"}
        if not required_fields.issubset(request.data):
            return Response({"Status": False, "Errors": "Не указаны все необходимые аргументы"},
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            token = ConfirmEmailToken.objects.get(user__email=request.data["email"], key=request.data["token"])
        except ConfirmEmailToken.DoesNotExist:
            return Response({"Status": False, "Errors": "Неверный токен или email"}, status=status.HTTP_400_BAD_REQUEST)

        user = token.user
        user.is_active = True
        user.save()
        token.delete()

        return Response({"Status": True, "Message": "Email успешно подтверждён. Теперь вы можете войти в систему."},
                        status=status.HTTP_200_OK)


class LoginAccount(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [UserRateThrottle, AnonRateThrottle]
    throttle_scope = 'account'

    @extend_schema(
        summary="Авторизация пользователя",
        description="Вход пользователя и получение токена для работы с API",
        request=LoginAccountRequestSerializer,
        responses={200: LoginAccountResponseSerializer, 400: ErrorResponseSerializer},
        tags=["Пользователи"],
    )
    def post(self, request, *args, **kwargs):
        required_fields = {"email", "password"}
        if not required_fields.issubset(request.data):
            return Response({"Status": False, "Errors": "Не указаны все необходимые аргументы"}, status=400)

        user = authenticate(request, username=request.data["email"], password=request.data["password"])
        if user and user.is_active:
            token, _ = Token.objects.get_or_create(user=user)
            return Response({"Status": True, "Token": token.key, "Message": "Запишите ваш токен для работы с API"},
                            status=200)

        return Response({"Status": False, "Errors": "Не удалось авторизовать"}, status=400)


class AccountDetails(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]
    throttle_scope = 'account'

    @extend_schema(
        summary="Просмотр данных пользователя",
        description="Получение данных текущего пользователя",
        responses=UserSerializer,
        tags=["Пользователи"],
    )
    def get(self, request, *args, **kwargs):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    @extend_schema(
        summary="Изменение данных пользователя",
        description="Изменение данных пользователя, включая возможность смены пароля и аватара",
        request=UserSerializer,
        responses={200: {"Status": True}, 400: ErrorResponseSerializer},
        tags=["Пользователи"],
    )
    def post(self, request, *args, **kwargs):
        if "password" in request.data:
            try:
                validate_password(request.data["password"])
            except Exception as password_error:
                return Response({"Status": False, "Errors": {"password": list(password_error)}}, status=400)
            request.user.set_password(request.data["password"])

        serializer_data = request.data.copy()
        if request.FILES.get("avatar"):
            serializer_data["avatar"] = request.FILES["avatar"]

        serializer = UserSerializer(request.user, data=serializer_data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"Status": True}, status=200)
        return Response({"Status": False, "Errors": serializer.errors}, status=400)

User = get_user_model()

class UserLoginView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [UserRateThrottle, AnonRateThrottle]
    throttle_scope = 'account'

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response({"Status": False, "Errors": "Email and password required"},
                            status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(request, username=email, password=password)

        if not user or not user.is_active:
            return Response({"Status": False}, status=status.HTTP_401_UNAUTHORIZED)

        token, _ = Token.objects.get_or_create(user=user)
        return Response({"Status": True, "Token": token.key, "Message": "Вы успешно вошли в систему"},
                        status=status.HTTP_200_OK)