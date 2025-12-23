"""
Кастомные валидаторы для приложения.
"""
import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_phone_number(value):
    """
    Валидация номера телефона.
    Поддерживает:
    - +7XXXXXXXXXX
    - +XXXXXXXXXXX (любые международные номера)
    - 8XXXXXXXXXX (российские номера)
    """
    cleaned_value = value.replace(' ', '').replace('-', '')

    pattern = r'^(?:\+7\d{10}|\+?\d{11,15}|8\d{10})$'
    
    if not re.match(pattern, cleaned_value):
        raise ValidationError(
            _('Введите корректный номер телефона (например: +79001234567)'),
            code='invalid_phone'
        )


def validate_password_strength(password):
    """
    Валидация силы пароля.
    """
    if len(password) < 8:
        raise ValidationError(
            _('Пароль должен содержать минимум 8 символов'),
            code='password_too_short'
        )
    
    if not re.search(r'[A-Z]', password):
        raise ValidationError(
            _('Пароль должен содержать хотя бы одну заглавную букву'),
            code='password_no_upper'
        )
    
    if not re.search(r'[a-z]', password):
        raise ValidationError(
            _('Пароль должен содержать хотя бы одну строчную букву'),
            code='password_no_lower'
        )
    
    if not re.search(r'\d', password):
        raise ValidationError(
            _('Пароль должен содержать хотя бы одну цифру'),
            code='password_no_digit'
        )


def validate_positive_quantity(value):
    """
    Валидация положительного количества.
    
    """
    if value <= 0:
        raise ValidationError(
            _('Количество должно быть больше нуля'),
            code='invalid_quantity'
        )


def validate_positive_price(value):
    """
    Валидация положительной цены.
    
    """
    if value <= 0:
        raise ValidationError(
            _('Цена должна быть больше нуля'),
            code='invalid_price'
        )


def validate_email_domain(value):
    """
    Валидация домена email.
    
    """
    allowed_domains = ['gmail.com', 'yandex.ru', 'mail.ru', 'outlook.com']
    domain = value.split('@')[-1].lower()
    
    if domain not in allowed_domains:
        raise ValidationError(
            _('Разрешены только email адреса с доменами: %(domains)s'),
            params={'domains': ', '.join(allowed_domains)},
            code='invalid_email_domain'
        )