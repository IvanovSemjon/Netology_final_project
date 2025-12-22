"""
Кастомный обработчик.
"""

from rest_framework import status
from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    """
    Кастомный обработчик исключений для DRF API.
    """

    response = exception_handler(exc, context)

    if response is not None:
        response.data = {
            "status": False,
            "error": response.data.get("detail", str(response.data)),
            "status_code": response.status_code,
        }

    return response


class APIException(Exception):
    """
    Базовое пользовательское исключение для API.
    """

    def __init__(self, message, status_code=status.HTTP_400_BAD_REQUEST):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class ValidationError(APIException):
    """
    Исключение для ошибок валидации.
    """

    def __init__(self, message):
        super().__init__(message, status.HTTP_400_BAD_REQUEST)


class AuthenticationError(APIException):
    """
    Исключение для ошибок аутентификации.
    """

    def __init__(self, message):
        super().__init__(message, status.HTTP_401_UNAUTHORIZED)


class PermissionError(APIException):
    """
    Исключение для ошибок доступа (403).
    """

    def __init__(self, message):
        super().__init__(message, status.HTTP_403_FORBIDDEN)
