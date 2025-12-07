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
        """Тест валидации корректных номеров телефонов"""
        valid_phones = [
            '+79001234567',
            '+12345678901',
            '89001234567'
        ]
        
        for phone in valid_phones:
            try:
                validate_phone_number(phone)
            except ValidationError:
                self.fail(f'Валидный номер {phone} не прошел валидацию')
    
    def test_validate_phone_number_invalid(self):
        """Тест валидации некорректных номеров телефонов"""
        invalid_phones = [
            '123',
            'abc',
            '+',
            '++79001234567',
            '8-900-123-45-67'
        ]
        
        for phone in invalid_phones:
            with self.assertRaises(ValidationError):
                validate_phone_number(phone)
    
    def test_validate_password_strength_valid(self):
        """Тест валидации сильных паролей"""
        valid_passwords = [
            'TestPass123',
            'MySecure1Pass',
            'Strong123Password'
        ]
        
        for password in valid_passwords:
            try:
                validate_password_strength(password)
            except ValidationError:
                self.fail(f'Валидный пароль {password} не прошел валидацию')
    
    def test_validate_password_strength_invalid(self):
        """Тест валидации слабых паролей"""
        invalid_passwords = [
            '123',  # Слишком короткий
            'password',  # Нет заглавных букв и цифр
            'PASSWORD',  # Нет строчных букв и цифр
            'Password',  # Нет цифр
            'password123',  # Нет заглавных букв
        ]
        
        for password in invalid_passwords:
            with self.assertRaises(ValidationError):
                validate_password_strength(password)
    
    def test_validate_positive_quantity_valid(self):
        """Тест валидации положительного количества"""
        valid_quantities = [1, 5, 100, 1000]
        
        for quantity in valid_quantities:
            try:
                validate_positive_quantity(quantity)
            except ValidationError:
                self.fail(f'Валидное количество {quantity} не прошло валидацию')
    
    def test_validate_positive_quantity_invalid(self):
        """Тест валидации неположительного количества"""
        invalid_quantities = [0, -1, -100]
        
        for quantity in invalid_quantities:
            with self.assertRaises(ValidationError):
                validate_positive_quantity(quantity)
    
    def test_validate_positive_price_valid(self):
        """Тест валидации положительной цены"""
        valid_prices = [1, 10.5, 100, 1000.99]
        
        for price in valid_prices:
            try:
                validate_positive_price(price)
            except ValidationError:
                self.fail(f'Валидная цена {price} не прошла валидацию')
    
    def test_validate_positive_price_invalid(self):
        """Тест валидации неположительной цены"""
        invalid_prices = [0, -1, -100.5]
        
        for price in invalid_prices:
            with self.assertRaises(ValidationError):
                validate_positive_price(price)