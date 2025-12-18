""" Celery задачи для асинхронного выполнения """
import yaml
from backend.models import (Category, Order, Parameter, Product, ProductInfo,
                            ProductParameter, Shop)
from backend.services.emails import send_order_status_email
from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from requests import get
from yaml import Loader as YamlLoader


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 3, "countdown": 10},
)
def send_email(self, subject, message, from_email, recipient_list):
    msg = EmailMultiAlternatives(
        subject=subject,
        body=message,
        from_email=from_email,
        to=recipient_list,
    )
    msg.send()


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 3, "countdown": 10},
)
def send_order_status_email_task(self, order_id: int) -> None:
    """
    Отправка email при изменении статуса заказа.
    """
    order = Order.objects.get(id=order_id)
    send_order_status_email(order)



@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 3, "countdown": 30},
)
def do_import(self, url: str) -> None:
    """
    Асинхронный импорт товаров из YAML-файла.
    """
    response = get(url, timeout=30)
    response.raise_for_status()

    data = yaml.load(response.content, Loader=YamlLoader)

    shop, _ = Shop.objects.get_or_create(
        name=data["shop"],
        defaults={"is_accepting_orders": True},
    )

    # Категории
    for category_data in data["categories"]:
        category, _ = Category.objects.get_or_create(
            id=category_data["id"],
            defaults={"name": category_data["name"]},
        )
        category.shops.add(shop)

    # Очистка старых товаров
    ProductInfo.objects.filter(shop=shop).delete()

    # Товары
    for item in data["goods"]:
        product, _ = Product.objects.get_or_create(
            name=item["name"],
            defaults={"category_id": item["category"]},
        )

        product_info = ProductInfo.objects.create(
            product=product,
            shop=shop,
            external_id=item["id"],
            model=item["model"],
            price=item["price"],
            price_rrc=item["price_rrc"],
            quantity=item["quantity"],
        )

        for param_name, param_value in item["parameters"].items():
            parameter, _ = Parameter.objects.get_or_create(name=param_name)

            ProductParameter.objects.create(
                product_info=product_info,
                parameter=parameter,
                value=str(param_value),
            )