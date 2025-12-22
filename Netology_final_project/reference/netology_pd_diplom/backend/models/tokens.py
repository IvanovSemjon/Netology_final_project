"""
Модели для токенов подтверждения.
"""
import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from .users import User


class ConfirmEmailToken(models.Model):
    """
    Токен для подтверждения email при регистрации.
    """
    
    user = models.ForeignKey(
        User,
        related_name='confirm_email_tokens',
        on_delete=models.CASCADE,
        verbose_name=_("User")
    )
    
    key = models.UUIDField(
        _("Key"),
        default=uuid.uuid4,
        unique=True,
        db_index=True
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Created at")
    )
    
    class Meta:
        verbose_name = _('Токен подтверждения email')
        verbose_name_plural = _('Токены подтверждения email')
    
    def __str__(self):
        return f"Email confirmation token for {self.user.email}"