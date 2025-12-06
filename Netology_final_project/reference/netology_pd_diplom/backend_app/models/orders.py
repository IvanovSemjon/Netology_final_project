"""Модели относящиеся к заказам"""
from django.db import models
from django.db.models import F, Sum
from django.utils.translation import gettext_lazy as _

from .catalog import ProductInfo
from .users import User


class OrderState(models.TextChoices):
    """Модель статуса заказа"""
    BASKET = "basket", _("Корзина")
    NEW = "new", _("Новый")
    CONFIRMED = "confirmed", _("Подтвержден")
    ASSEMBLED = "assembled", _("Собран")
    SENT = "sent", _("Отправлен")
    DELIVERED = "delivered", _("Доставлен")
    CANCELED = "canceled", _("Отменен")


class Order(models.Model):
    """
    Модель заказа.

    Управляет жизненным циклом заказа от корзины до доставки,
    включая резервирование товаров и отправку уведомлений.
    """
    user = models.ForeignKey(
        User, related_name="orders", null=True, blank=True, on_delete=models.SET_NULL
        )
    dt = models.DateTimeField(auto_now_add=True)
    state = models.CharField(_("state"),
                             max_length=20,
                             choices=OrderState.choices,
                               default=OrderState.BASKET
                               )
    contact = models.ForeignKey("backend.Contact",
                                 null=True,
                                 blank=True,
                                 on_delete=models.SET_NULL
                                 )

    admin_email_sent = models.BooleanField(default=False)
    client_email_sent = models.BooleanField(default=False)

    class Meta:
        """Метаданные модели Order"""
        verbose_name = _("Заказ")
        verbose_name_plural = _("Заказы")
        ordering = ("-dt",)
        indexes = [
            models.Index(fields=["state"]),
            models.Index(fields=["dt"]),
            models.Index(fields=["user"]),
            models.Index(fields=["user", "state"]),
        ]

    def __str__(self) -> str:
        """Строковое представление модели Order"""
        return f"Заказ #{self.pk} создан {self.dt}"

    def get_total_sum(self):
        """Получить общую сумму заказа"""
        try:
            return (
                self.ordered_items.aggregate(
                    total=Sum(F("quantity") * F("product_info__price"))
                )["total"]
                or 0
            )
        except AttributeError:
            return 0

    def get_items_count(self):
        """Получить общее количество товаров в заказе"""
        try:
            return self.ordered_items.aggregate(total=Sum("quantity"))["total"] or 0
        except AttributeError:
            return 0


class OrderItem(models.Model):
    """
    Позиция в заказе.

    Связывает заказ с конкретным товаром и его количеством.
    Каждая позиция представляет один тип товара в заказе.
    """
    order = models.ForeignKey(
        Order, related_name="ordered_items", on_delete=models.CASCADE
        )
    product_info = models.ForeignKey(
        ProductInfo, related_name="ordered_items", on_delete=models.CASCADE
        )
    quantity = models.PositiveIntegerField(verbose_name="Количество")

    class Meta:
        """Метаданные модели OrderItem"""
        verbose_name = _("Заказ")
        verbose_name_plural = _("Список заказов")
        constraints = [
            models.UniqueConstraint(fields=["order", "product_info"], name="unique_order_item")
        ]
        indexes = [
            models.Index(fields=["order"]),
            models.Index(fields=["order", "product_info"]),
        ]

    def __str__(self) -> str:
        """Строковое представление модели OrderItem"""
        try:
            product_name = self.product_info.product.name
        except (AttributeError, TypeError):
            product_name = "Неизвестный продукт"
        return f"{product_name} - {self.quantity} шт."

    def get_total_price(self):
        """Получить общую стоимость позиции"""
        try:
            return self.quantity * self.product_info.price
        except (AttributeError, TypeError):
            return 0

class OrderStatusHistory(models.Model):
    """
    История изменений статуса заказа.
    Хранит предыдущий и новый статусы, кто изменил и комментарий.
    """

    order = models.ForeignKey(
        Order,
        related_name="status_history",
        on_delete=models.CASCADE,
        verbose_name=_("order"),
    )
    old_status = models.CharField(
        _("old status"), max_length=20, choices=OrderState.choices
    )
    new_status = models.CharField(
        _("new status"), max_length=20, choices=OrderState.choices
    )
    changed_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("changed by")
    )
    changed_at = models.DateTimeField(auto_now_add=True, verbose_name=_("changed at"))
    comment = models.TextField(blank=True, verbose_name=_("comment"))

    class Meta:
        """Метаданные модели Contact"""
        verbose_name = _("order status history")
        verbose_name_plural = _("order status histories")
        ordering = ("-changed_at",)
        indexes = [
            models.Index(fields=["order", "changed_at"]),
            models.Index(fields=["old_status"]),
            models.Index(fields=["new_status"]),
        ]

    def __str__(self) -> str:
        order_id = getattr(self.order, "pk", "unknown")
        return f"Order {order_id}: {self.old_status} → {self.new_status}"