from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


def custom_exception_handler(exc, context):
    """
    Кастомный обработчик исключений для API
    """
    response = exception_handler(exc, context)

    if response is not None:
        custom_response_data = {
            'Status': False,
            'Error': response.data.get('detail', str(response.data)),
            'status_code': response.status_code
        }
        response.data = custom_response_data

    return response


class APIException(Exception):
    """
    Базовое исключение для API
    """
    def __init__(self, message, status_code=status.HTTP_400_BAD_REQUEST):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class ValidationError(APIException):
    """
    Исключение для ошибок валидации
    """
    def __init__(self, message):
        super().__init__(message, status.HTTP_400_BAD_REQUEST)


class AuthenticationError(APIException):
    """
    Исключение для ошибок аутентификации
    """
    def __init__(self, message):
        super().__init__(message, status.HTTP_401_UNAUTHORIZED)


class PermissionError(APIException):
    """
    Исключение для ошибок доступа
    """
    def __init__(self, message):
        super().__init__(message, status.HTTP_403_FORBIDDEN)