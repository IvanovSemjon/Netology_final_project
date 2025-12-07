"""Сервисы для отправки email"""
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.urls import reverse
from backend.models import ConfirmEmailToken


def send_confirmation_email(user):
    """Отправка email для подтверждения регистрации"""
    try:
        token, created = ConfirmEmailToken.objects.get_or_create(user=user)
        
        subject = 'Подтверждение регистрации'
        confirmation_url = f"{settings.FRONTEND_URL}/confirm-email/{token.key}/"
        
        message = render_to_string('emails/confirm_registration.html', {
            'user': user,
            'confirmation_url': confirmation_url,
        })
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=message,
            fail_silently=True,  # Не падаем при ошибке отправки
        )
        return True
    except Exception as e:
        print(f"Ошибка отправки email: {e}")
        return False


def send_order_confirmation_email(order):
    """Отправка email о подтверждении заказа"""
    subject = f'Заказ #{order.id} подтвержден'
    
    message = render_to_string('emails/order_confirmation.html', {
        'order': order,
        'user': order.user,
    })
    
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[order.user.email],
        html_message=message,
        fail_silently=False,
    )


def send_order_status_email(order):
    """Отправка email об изменении статуса заказа"""
    subject = f'Статус заказа #{order.id} изменен'
    
    message = render_to_string('emails/order_status.html', {
        'order': order,
        'user': order.user,
    })
    
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[order.user.email],
        html_message=message,
        fail_silently=False,
    )