"""
Вспомогательные функции для приложения backend
"""
from django.utils.encoding import force_str
from django.http import JsonResponse
from rest_framework import status


def strtobool(val):
    """
    Преобразует строку в boolean (аналог distutils.strtobool)
    """
    val = force_str(val).lower()
    if val in ('y', 'yes', 't', 'true', 'on', '1'):
        return True
    elif val in ('n', 'no', 'f', 'false', 'off', '0'):
        return False
    else:
        raise ValueError(f"Invalid truth value: {val}")


def success_response(message="Success", data=None, status_code=status.HTTP_200_OK):
    """
    Стандартный успешный ответ API
    """
    response_data = {'Status': True, 'Message': message}
    if data:
        response_data['Data'] = data
    return JsonResponse(response_data, status=status_code)


def error_response(message="Error", status_code=status.HTTP_400_BAD_REQUEST):
    """
    Стандартный ответ об ошибке API
    """
    return JsonResponse(
        {'Status': False, 'Error': message}, 
        status=status_code
    )


def validate_required_fields(data, required_fields):
    """
    Проверяет наличие обязательных полей в данных
    """
    missing_fields = []
    for field in required_fields:
        if field not in data or not data[field]:
            missing_fields.append(field)
    
    if missing_fields:
        raise ValueError(f"Отсутствуют обязательные поля: {', '.join(missing_fields)}")
    
    return True