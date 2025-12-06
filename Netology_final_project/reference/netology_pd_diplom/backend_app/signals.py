"""Сигналы Django для обработки событий системы"""
# pylint: disable=no-member,unused-argument
from typing import Type

from django.db.models.signals import post_save
from django.dispatch import receiver, Signal
from django_rest_passwordreset.signals import reset_password_token_created
from django.conf import settings

from backend.models.users import User
from backend.models import Order
from backend.services.emails import send_order_status_email, send_confirmation_email
from backend.tasks.celery_tasks import send_email


# Кастомные сигналы
new_user_registered = Signal()
new_order = Signal()
order_status_changed = Signal()


@receiver(reset_password_token_created)
def password_reset_token_created_handler(sender, instance, reset_password_token, **kwargs):
    """
    Отправляет письмо со сбросом пароля через Celery.
    
    Args:
        reset_password_token: Токен для сброса пароля
    """
    subject = f"Сброс пароля для {reset_password_token.user.email}"
    message = f"Ваш токен для сброса пароля: {reset_password_token.key}"
    
    # Используем Celery для асинхронной отправки
    send_email.delay(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[reset_password_token.user.email]
    )


@receiver(post_save, sender=Order)
def order_status_changed_handler(sender, instance, created, **kwargs):
    """Отправка email при изменении статуса заказа"""
    if not created and instance.state != 'basket':
        send_order_status_email(instance)









