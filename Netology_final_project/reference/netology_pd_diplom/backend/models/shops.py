"""Модели относящиеся к магазинам"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from .users import User


class Shop(models.Model):
    """
    Модель магазина.

    Представляет магазин-партнер с возможностью управления
    статусом приема заказов и привязкой к пользователю.
    """
    name = models.CharField(_("name"), max_length=50)
    url = models.URLField(_("url"), null=True, blank=True)
    user = models.OneToOneField(
        User, verbose_name=_("user"), null=True, blank=True, on_delete=models.CASCADE)
    is_accepting_orders = models.BooleanField(_("accepting orders"), default=True)

    class Meta:
        """Метаданные модели Shop"""
        verbose_name = _("Магазин")
        verbose_name_plural = _("Магазины")
        ordering = ("name",)
        indexes = [models.Index(fields=["is_accepting_orders"])]

    def __str__(self) -> str:
        """Строковое представление модели Shop"""
        return str(self.name)