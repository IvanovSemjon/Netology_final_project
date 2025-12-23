"""Тесты для валидаторов"""
from django.test import TestCase
from django.core.exceptions import ValidationError
from backend.validators import (
    validate_phone_number,
    validate_password_strength,
    validate_positive_quantity,
    validate_positive_price
)


class ValidatorsTestCase(TestCase):
    """Тесты кастомных валидаторов"""

    def test_validate_phone_number_valid(self):
        """Корректные номера телефонов"""
        valid_phones = [
            '+79001234567',
            '+12345678901',
            '89001234567'
        ]
        for phone in valid_phones:
            try:
                validate_phone_number(phone)
            except ValidationError:
                self.fail(f"Валидный номер {phone} не прошел валидацию")

    def test_validate_phone_number_invalid(self):
        """Некорректные номера телефонов"""
        invalid_phones = [
            '123',
            'abc',
            '+',
            '++79001234567',
            '8-900-123-45-67'
        ]
        for phone in invalid_phones:
            with self.assertRaises(ValidationError, msg=f"Номер {phone} должен быть некорректным"):
                validate_phone_number(phone)

    def test_validate_password_strength_valid(self):
        """Сильные пароли"""
        valid_passwords = [
            'TestPass123',
            'MySecure1Pass',
            'Strong123Password'
        ]
        for pwd in valid_passwords:
            try:
                validate_password_strength(pwd)
            except ValidationError:
                self.fail(f"Валидный пароль {pwd} не прошел валидацию")

    def test_validate_password_strength_invalid(self):
        """Слабые пароли"""
        invalid_passwords = [
            '123',
            'password',
            'PASSWORD',
            'Password',
            'password123',
        ]
        for pwd in invalid_passwords:
            with self.assertRaises(ValidationError, msg=f"Пароль {pwd} должен быть некорректным"):
                validate_password_strength(pwd)

    def test_validate_positive_quantity_valid(self):
        """Положительное количество"""
        for qty in [1, 5, 100, 1000]:
            try:
                validate_positive_quantity(qty)
            except ValidationError:
                self.fail(f"Валидное количество {qty} не прошло валидацию")

    def test_validate_positive_quantity_invalid(self):
        """Неположительное количество"""
        for qty in [0, -1, -100]:
            with self.assertRaises(ValidationError, msg=f"Количество {qty} должно быть некорректным"):
                validate_positive_quantity(qty)

    def test_validate_positive_price_valid(self):
        """Положительная цена"""
        for price in [1, 10.5, 100, 1000.99]:
            try:
                validate_positive_price(price)
            except ValidationError:
                self.fail(f"Валидная цена {price} не прошла валидацию")

    def test_validate_positive_price_invalid(self):
        """Неположительная цена"""
        for price in [0, -1, -100.5]:
            with self.assertRaises(ValidationError, msg=f"Цена {price} должна быть некорректной"):
                validate_positive_price(price)