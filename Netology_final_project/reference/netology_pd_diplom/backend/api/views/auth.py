from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.http import JsonResponse
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView

from backend.models import User, ConfirmEmailToken
from backend.api.serializers.user import UserSerializer
from backend.services.emails import send_confirmation_email


class RegisterAccount(APIView):
    """
    Регистрация пользователей
    """

    def post(self, request, *args, **kwargs):
        if {'first_name', 'last_name', 'email', 'password', 'company', 'position'}.issubset(request.data):
            try:
                validate_password(request.data['password'])
            except Exception as password_error:
                return JsonResponse(
                    {'Status': False, 'Errors': {'password': list(password_error)}}
                )

            user_serializer = UserSerializer(data=request.data)
            if not user_serializer.is_valid():
                return JsonResponse({'Status': False, 'Errors': user_serializer.errors})

            user = user_serializer.save()
            user.set_password(request.data['password'])
            user.is_active = False
            user.save()

            # Асинхронная отправка email подтверждения
            send_confirmation_email_task.delay(user.id)

            return JsonResponse({
                'Status': True,
                'Message': (
                    f'Пользователь {user.first_name} {user.last_name} создан. '
                    'Проверьте email для подтверждения регистрации.'
                )
            })

        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})


class ConfirmAccount(APIView):
    """
    Подтверждение email
    """

    def post(self, request, *args, **kwargs):
        if {'email', 'token'}.issubset(request.data):
            try:
                token = ConfirmEmailToken.objects.get(
                    user__email=request.data['email'],
                    key=request.data['token'],
                )
            except ConfirmEmailToken.DoesNotExist:
                return JsonResponse({'Status': False, 'Error': 'Неверный токен или email'})

            user = token.user
            user.is_active = True
            user.save()
            token.delete()

            return JsonResponse({
                'Status': True,
                'Message': 'Email успешно подтверждён. Теперь вы можете войти в систему.'
            })

        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})


class LoginAccount(APIView):
    """
    Авторизация пользователей
    """

    def post(self, request, *args, **kwargs):
        if {'email', 'password'}.issubset(request.data):
            user = authenticate(
                request,
                username=request.data['email'],
                password=request.data['password'],
            )

            if user and user.is_active:
                token, _ = Token.objects.get_or_create(user=user)
                return JsonResponse({
                    'Status': True,
                    'Token': token.key,
                    'Message': 'Запишите ваш токен для работы с API',
                })

            return JsonResponse({'Status': False, 'Errors': 'Не удалось авторизовать'})

        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})


class AccountDetails(APIView):
    """
    Управление данными аккаунта
    """

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Требуется авторизация'}, status=403)

        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Требуется авторизация'}, status=403)

        if 'password' in request.data:
            try:
                validate_password(request.data['password'])
            except Exception as password_error:
                return JsonResponse(
                    {'Status': False, 'Errors': {'password': list(password_error)}}
                )
            request.user.set_password(request.data['password'])

        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse({'Status': True})

        return JsonResponse({'Status': False, 'Errors': serializer.errors})