"""
Константы для приложения backend.

"""

# Типы пользователей
USER_TYPE_CHOICES = [
    ('shop', 'Магазин'),
    ('buyer', 'Покупатель'),
]

# Статусы заказов
ORDER_STATE_CHOICES = [
    ('basket', 'Статус корзины'),
    ('new', 'Новый'),
    ('confirmed', 'Подтвержден'),
    ('assembled', 'Собран'),
    ('sent', 'Отправлен'),
    ('delivered', 'Доставлен'),
    ('canceled', 'Отменен'),
]

# Статусы магазинов
SHOP_STATE_CHOICES = [
    (True, 'Принимает заказы'),
    (False, 'Не принимает заказы'),
]

# Сообщения об ошибках
ERROR_MESSAGES = {
    'LOGIN_REQUIRED': 'Необходима авторизация',
    'INVALID_CREDENTIALS': 'Неверные учетные данные',
    'MISSING_ARGUMENTS': 'Не указаны все необходимые аргументы',
    'SHOP_ONLY': 'Только для магазинов',
    'BUYER_ONLY': 'Только для покупателей',
    'INVALID_FORMAT': 'Неверный формат данных',
    'PERMISSION_DENIED': 'Доступ запрещен',
}

# Успешные сообщения
SUCCESS_MESSAGES = {
    'CREATED': 'Успешно создано',
    'UPDATED': 'Успешно обновлено',
    'DELETED': 'Успешно удалено',
    'OPERATION_SUCCESS': 'Операция выполнена успешно',
}