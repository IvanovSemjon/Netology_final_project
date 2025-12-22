"""
Модели относящиеся к категориям.
"""
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from .shops import Shop


class Category(models.Model):
    """
    Модель категории товаров.

    Категории могут быть связаны с несколькими магазинами
    и содержать различные продукты.
    """
    name = models.CharField(_("name"), max_length=40)
    shops = models.ManyToManyField(Shop, related_name="categories", blank=True)

    class Meta:
        """Метаданные модели Category"""
        verbose_name = _("Категория")
        verbose_name_plural = _("Категории")
        ordering = ("name",)

    def __str__(self) -> str:
        """Строковое представление модели Category"""
        return str(self.name)


class Product(models.Model):
    """
    Модель продукта.

    Базовая информация о товаре, включая название и категорию.
    Конкретная информация о цене и наличии хранится в ProductInfo.
    """
    name = models.CharField(_("name"), max_length=80)
    category = models.ForeignKey(
        Category, related_name="products", null=True, blank=True, on_delete=models.SET_NULL
        )

    class Meta:
        """
        Метаданные модели Product.
        """
        verbose_name = _("Товар")
        verbose_name_plural = _("Товары")
        ordering = ("name",)
        indexes = [models.Index(fields=["category"])]

    def __str__(self) -> str:
        """
        Строковое представление модели Product.
        """
        return str(self.name)


class ProductInfo(models.Model):
    """
    Информация о продукте в конкретном магазине.

    Содержит данные о цене, количестве, модели и внешнем ID
    для каждого продукта в каждом магазине.
    """
    model = models.CharField(_("model"), max_length=80, blank=True)
    external_id = models.PositiveIntegerField(_("external id"))
    product = models.ForeignKey(Product, related_name="product_infos", on_delete=models.CASCADE)
    shop = models.ForeignKey(Shop, related_name="product_infos", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(_("quantity"), default=0)
    price = models.DecimalField(_("price"), max_digits=10, decimal_places=2)
    price_rrc = models.DecimalField(_("price rrc"), max_digits=10, decimal_places=2)

    class Meta:
        """
        Метаданнные модели ProductInfo.
        """
        verbose_name = _("Информация о товаре")
        verbose_name_plural = _("Информация о товарах")
        constraints = [models.UniqueConstraint(fields=["product",
                                            "shop", 
                                            "external_id"
                                            ], name="unique_product_info")
        ]
        indexes = [
            models.Index(fields=["shop", "product"]),
            models.Index(fields=["external_id"]),
            models.Index(fields=["shop", "price"]),
            models.Index(fields=["shop", "quantity"]),
        ]

    def __str__(self) -> str:
        """
        Строковое представление модели ProductInfo.
        """
        return f"{self.product.name} — {self.shop.name}"

    @property
    def available(self) -> bool:
        """
        Доступно ли для заказа.
        """
        return self.quantity > 0

    def check_availability(self, quantity: int) -> bool:
        """
        Проверить доступность указанного количества.
        """
        if not isinstance(quantity, int) or quantity < 0:
            return False
        return self.quantity >= quantity

    def clean(self) -> None:
        """
        Валидация модели.
        """
        if self.price <= 0:
            raise ValidationError(_("Price must be > 0"))
        if self.price_rrc <= 0:
            raise ValidationError(_("RRC price must be > 0"))
