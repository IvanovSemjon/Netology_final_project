from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.http import JsonResponse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView

from backend.models import User, ConfirmEmailToken
from backend.tasks.celery_tasks import send_confirmation_email_task
from backend.api.serializers.user import UserSerializer
from backend.services.emails import send_confirmation_email


class RegisterAccount(APIView):
    """
    Для регистрации покупателей
    """

    def post(self, request, *args, **kwargs):
        """
        Process a POST request and create a new user.
        """
        if {'first_name', 'last_name', 'email', 'password', 'company', 'position'}.issubset(request.data):
            try:
                validate_password(request.data['password'])
            except Exception as password_error:
                error_array = []
                for item in password_error:
                    error_array.append(item)
                return JsonResponse({'Status': False, 'Errors': {'password': error_array}})
            else:
                user_serializer = UserSerializer(data=request.data)
                if user_serializer.is_valid():
                    user = user_serializer.save()
                    user.set_password(request.data['password'])
                    user.save()
                    
                    # Отправляем email для подтверждения
                    email_sent = send_confirmation_email(user)
                    
                    if email_sent:
                        message = f'Пользователь {user.first_name} {user.last_name} создан. Проверьте email для подтверждения регистрации.'
                    else:
                        message = f'Пользователь {user.first_name} {user.last_name} создан. Email подтверждения не отправлен (проблемы с почтовым сервером).'
                    
                    return JsonResponse({
                        'Status': True, 
                        'Message': message
                    })
                else:
                    return JsonResponse({'Status': False, 'Errors': user_serializer.errors})

        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})


class ConfirmAccount(APIView):
    """
    Класс для подтверждения почтового адреса
    """

    def post(self, request, *args, **kwargs):
        """
        Подтверждает почтовый адрес пользователя.
        """
        if {'email', 'token'}.issubset(request.data):
            try:
                token = ConfirmEmailToken.objects.get(
                    user__email=request.data['email'],
                    key=request.data['token']
                )
                user = token.user
                user.is_active = True
                user.save()
                token.delete()
                
                return JsonResponse({
                    'Status': True, 
                    'Message': 'Email успешно подтвержден. Теперь вы можете войти в систему.'
                })
            except ConfirmEmailToken.DoesNotExist:
                return JsonResponse({
                    'Status': False, 
                    'Error': 'Неверный токен или email'
                })

        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})


class LoginAccount(APIView):
    """
    Класс для авторизации пользователей
    """

    def post(self, request, *args, **kwargs):
        """
        Authenticate a user.
        """
        if {'email', 'password'}.issubset(request.data):
            user = authenticate(request, username=request.data['email'], password=request.data['password'])

            if user is not None:
                if user.is_active:
                    token, _ = Token.objects.get_or_create(user=user)
                    return JsonResponse({
                        'Status': True, 
                        'Token': token.key,
                        'Message': 'Запишите Ваш токен для работы с данным сайтом'
                    })

            return JsonResponse({'Status': False, 'Errors': 'Не удалось авторизовать'})

        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})


class AccountDetails(APIView):
    """
    A class for managing user account details.
    """

    def get(self, request, *args, **kwargs):
        """
        Retrieve the details of the authenticated user.
        """
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)

        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        """
        Update the account details of the authenticated user.
        """
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)

        if 'password' in request.data:
            try:
                validate_password(request.data['password'])
            except Exception as password_error:
                error_array = []
                for item in password_error:
                    error_array.append(item)
                return JsonResponse({'Status': False, 'Errors': {'password': error_array}})
            else:
                request.user.set_password(request.data['password'])

        user_serializer = UserSerializer(request.user, data=request.data, partial=True)
        if user_serializer.is_valid():
            user_serializer.save()
            return JsonResponse({'Status': True})
        else:
            return JsonResponse({'Status': False, 'Errors': user_serializer.errors})