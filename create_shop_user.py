#!/usr/bin/env python
"""
Скрипт для создания пользователя-магазина
"""
import os
import sys
import django

# Добавляем путь к проекту
sys.path.append('c:\\STUDY_2025\\Netology\\netology_final\\Netology_final_project\\reference\\netology_pd_diplom')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'netology_pd_diplom.settings')
django.setup()

from backend.models import User, Shop

# Создаем пользователя-магазин
shop_user = User.objects.create_user(
    email='shop@example.com',
    password='ShopPass123',
    first_name='Магазин',
    last_name='Тестовый',
    type='shop',
    is_active=True
)

# Создаем объект магазина
shop = Shop.objects.create(
    name='Тестовый магазин',
    user=shop_user,
    is_accepting_orders=True
)

print(f"Создан пользователь: {shop_user.email}")
print(f"Создан магазин: {shop.name}")
print(f"Для входа используйте:")
print(f"Email: {shop_user.email}")
print(f"Password: ShopPass123")