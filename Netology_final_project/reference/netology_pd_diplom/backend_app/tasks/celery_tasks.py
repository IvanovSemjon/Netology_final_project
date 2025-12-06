"""
Celery задачи для асинхронного выполнения
"""
import yaml
from yaml import Loader as YamlLoader
from requests import get
from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.conf import settings

from backend.models import Shop, Category, Product, ProductInfo, Parameter, ProductParameter


@shared_task
def send_email(subject, message, from_email, recipient_list):
    """
    Асинхронная отправка email
    
    Args:
        subject: Тема письма
        message: Текст письма
        from_email: Email отправителя
        recipient_list: Список получателей
    """
    try:
        msg = EmailMultiAlternatives(
            subject=subject,
            body=message,
            from_email=from_email,
            to=recipient_list
        )
        msg.send()
        return f"Email отправлен успешно: {recipient_list}"
        
    except Exception as e:
        return f"Ошибка отправки email: {str(e)}"


@shared_task
def do_import(url):
    """
    Асинхронный импорт товаров из YAML файла
    
    Args:
        url: URL для загрузки данных
        
    Returns:
        dict: Результат импорта
    """
    try:
        # Загружаем данные
        response = get(url, timeout=30)
        response.raise_for_status()
        
        data = yaml.load(response.content, Loader=YamlLoader)
        
        # Создаем или получаем магазин
        shop, created = Shop.objects.get_or_create(
            name=data['shop'],
            defaults={'is_accepting_orders': True}
        )
        
        # Обрабатываем категории
        categories_created = 0
        for category_data in data['categories']:
            category, created = Category.objects.get_or_create(
                id=category_data['id'],
                defaults={'name': category_data['name']}
            )
            category.shops.add(shop)
            if created:
                categories_created += 1
        
        # Удаляем старые товары этого магазина
        old_products_count = ProductInfo.objects.filter(shop=shop).count()
        ProductInfo.objects.filter(shop=shop).delete()
        
        # Обрабатываем товары
        products_created = 0
        parameters_created = 0
        
        for item in data['goods']:
            # Создаем или получаем продукт
            product, created = Product.objects.get_or_create(
                name=item['name'],
                defaults={'category_id': item['category']}
            )
            
            # Создаем информацию о продукте
            product_info = ProductInfo.objects.create(
                product=product,
                shop=shop,
                external_id=item['id'],
                model=item['model'],
                price=item['price'],
                price_rrc=item['price_rrc'],
                quantity=item['quantity']
            )
            products_created += 1
            
            # Обрабатываем параметры
            for param_name, param_value in item['parameters'].items():
                parameter, created = Parameter.objects.get_or_create(
                    name=param_name
                )
                
                ProductParameter.objects.create(
                    product_info=product_info,
                    parameter=parameter,
                    value=str(param_value)
                )
                parameters_created += 1
        
        result = {
            'status': 'success',
            'shop': shop.name,
            'categories_created': categories_created,
            'old_products_deleted': old_products_count,
            'products_created': products_created,
            'parameters_created': parameters_created,
            'message': f'Импорт завершен успешно для магазина {shop.name}'
        }
        
        return result
        
    except Exception as e:
        return {
            'status': 'error',
            'message': f'Ошибка импорта: {str(e)}'
        }