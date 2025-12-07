"""Тесты для аутентификации"""
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from backend.models import User, ConfirmEmailToken


class AuthTestCase(TestCase):
    """Тесты аутентификации и регистрации"""
    
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('api:user-register')
        self.login_url = reverse('api:user-login')
        self.confirm_url = reverse('api:user-register-confirm')
        
        self.valid_user_data = {
            'first_name': 'Тест',
            'last_name': 'Пользователь',
            'email': 'test@gmail.com',
            'password': 'TestPass123',
            'company': 'Тест Компания',
            'position': 'Тестер'
        }
    
    def test_user_registration_success(self):
        """Тест успешной регистрации пользователя"""
        response = self.client.post(self.register_url, self.valid_user_data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.json()['Status'])
        self.assertIn('Проверьте email', response.json()['Message'])
        
        # Проверяем, что пользователь создан
        user = User.objects.get(email=self.valid_user_data['email'])
        self.assertFalse(user.is_active)  # Должен быть неактивным до подтверждения
        
        # Проверяем, что создан токен подтверждения
        self.assertTrue(ConfirmEmailToken.objects.filter(user=user).exists())
    
    def test_user_registration_invalid_password(self):
        """Тест регистрации с невалидным паролем"""
        invalid_data = self.valid_user_data.copy()
        invalid_data['password'] = '123'  # Слишком простой пароль
        
        response = self.client.post(self.register_url, invalid_data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.json()['Status'])
        self.assertIn('password', response.json()['Errors'])
    
    def test_user_registration_duplicate_email(self):
        """Тест регистрации с существующим email"""
        # Создаем пользователя
        User.objects.create_user(
            email=self.valid_user_data['email'],
            password='TestPass123'
        )
        
        response = self.client.post(self.register_url, self.valid_user_data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.json()['Status'])
    
    def test_email_confirmation_success(self):
        """Тест успешного подтверждения email"""
        # Создаем пользователя
        user = User.objects.create_user(
            email=self.valid_user_data['email'],
            password='TestPass123',
            is_active=False
        )
        
        # Создаем токен подтверждения
        token = ConfirmEmailToken.objects.create(user=user)
        
        confirm_data = {
            'email': user.email,
            'token': str(token.key)
        }
        
        response = self.client.post(self.confirm_url, confirm_data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.json()['Status'])
        
        # Проверяем, что пользователь стал активным
        user.refresh_from_db()
        self.assertTrue(user.is_active)
        
        # Проверяем, что токен удален
        self.assertFalse(ConfirmEmailToken.objects.filter(key=token.key).exists())
    
    def test_login_success(self):
        """Тест успешного входа"""
        # Создаем активного пользователя
        user = User.objects.create_user(
            email=self.valid_user_data['email'],
            password=self.valid_user_data['password'],
            is_active=True
        )
        
        login_data = {
            'email': user.email,
            'password': self.valid_user_data['password']
        }
        
        response = self.client.post(self.login_url, login_data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.json()['Status'])
        self.assertIn('Token', response.json())
    
    def test_login_invalid_credentials(self):
        """Тест входа с неверными данными"""
        login_data = {
            'email': 'wrong@gmail.com',
            'password': 'wrongpass'
        }
        
        response = self.client.post(self.login_url, login_data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.json()['Status'])