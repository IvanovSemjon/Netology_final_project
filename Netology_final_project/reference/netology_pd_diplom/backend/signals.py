"""Сигналы Django для обработки событий системы"""
# pylint: disable=no-member,unused-argument

from django.conf import settings
from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import Signal, receiver
from django_rest_passwordreset.signals import reset_password_token_created

from backend.models import Order
from backend.tasks.celery_tasks import send_email, send_order_status_email_task

# Кастомные сигналы
new_user_registered = Signal()
new_order = Signal()
order_status_changed = Signal()


@receiver(reset_password_token_created)
def password_reset_token_created_handler(sender, instance, reset_password_token, **kwargs):
    """ Отправляет письмо со сбросом пароля через Celery. """
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
    if not created and instance.state != 'basket':
        transaction.on_commit(
            lambda: send_order_status_email_task.delay(instance.id)
        )
