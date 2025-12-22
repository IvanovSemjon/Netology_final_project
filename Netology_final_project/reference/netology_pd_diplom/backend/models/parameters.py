"""
Модели относящиеся к параметрам.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from .catalog import ProductInfo


class Parameter(models.Model):
    """
    Модель параметра товара.

    Определяет возможные характеристики товаров
    (например, цвет, размер, материал).
    """
    name = models.CharField(_("name"), max_length=40)

    class Meta:
        """
        Метаданные модели Parameter.
        """
        verbose_name = _("Название параметра")
        verbose_name_plural = _("Названия параметров")
        ordering = ("name",)

    def __str__(self) -> str:
        """
        Строковое представление модели Parameter.
        """
        return str(self.name)


class ProductParameter(models.Model):
    """
    Значение параметра для конкретного товара.

    Связывает ProductInfo с Parameter и хранит конкретное значение
    характеристики для данного товара в магазине.
    """
    product_info = models.ForeignKey(
        ProductInfo, related_name="product_parameters", on_delete=models.CASCADE
        )
    parameter = models.ForeignKey(
        Parameter, related_name="product_parameters", on_delete=models.CASCADE
        )
    value = models.CharField(_("value"), max_length=100)

    class Meta:
        """
        Метаданные модели ProductParameter.
        """
        verbose_name = _("Параметр продукта")
        verbose_name_plural = _("Список параметров")
        constraints = [models.UniqueConstraint(
                fields=["product_info", "parameter"],
                name="unique_product_parameter"
                )
                ]

    def __str__(self) -> str:
        """
        Строковое представление модели ProductParameter.
        """
        parameter_name = (
            self.parameter.name if self.parameter else "Неизвестный параметр"
        )
        return f"{parameter_name}: {self.value}"
