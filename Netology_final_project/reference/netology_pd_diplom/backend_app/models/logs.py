"""Модели связанные с логами"""
from django.db import models
from django.utils.translation import gettext_lazy as _

from .orders import Order
from .users import User


class EmailLog(models.Model):
    """
    Лог отправленных email сообщений.

    Ведет учет всех отправленных писем для аудита
    и отслеживания статуса доставки уведомлений.
    """
    EMAIL_TYPE_CHOICES = (
        ("order_confirmation", _("Order confirmation")),
        ("order_status", _("Order status")),
        ("admin_notification", _("Admin notification")),
        ("password_reset", _("Password reset")),
        ("email_confirmation", _("Email confirmation")),
    )

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    email = models.EmailField()
    subject = models.CharField(max_length=255)
    email_type = models.CharField(max_length=50, choices=EMAIL_TYPE_CHOICES)
    sent_at = models.DateTimeField(auto_now_add=True)
    status = models.BooleanField(default=True)
    error_message = models.TextField(blank=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        """Метаданные модели EmailLog"""
        verbose_name = _("email log")
        verbose_name_plural = _("email logs")
        ordering = ("-sent_at",)
        indexes = [
            models.Index(fields=["sent_at"]),
            models.Index(fields=["status"]),
            models.Index(fields=["email_type"])
            ]

    def __str__(self) -> str:
        """Строковое представление модели EmailLog"""
        return f"{self.email} — {self.subject}"
