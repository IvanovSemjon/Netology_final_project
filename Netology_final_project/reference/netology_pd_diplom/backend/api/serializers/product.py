"""
Сериализаторы товаров.
"""

from backend.models import Product, ProductInfo, ProductParameter
from rest_framework import serializers


class ProductSerializer(serializers.ModelSerializer):
    """
    Сериализатор для продукта.
    """

    category = serializers.StringRelatedField()

    class Meta:
        """
        Мета-класс.
        """

        model = Product
        fields = (
            "name",
            "category",
        )


class ProductParameterSerializer(serializers.ModelSerializer):
    """
    Сериализатор для параметров продукта.
    """

    parameter = serializers.StringRelatedField()

    class Meta:
        """
        Мета-класс.
        """

        model = ProductParameter
        fields = (
            "parameter",
            "value",
        )


class ProductInfoSerializer(serializers.ModelSerializer):
    """
    Сериализатор для информации о продукте.
    """

    product = ProductSerializer(read_only=True)
    product_parameters = ProductParameterSerializer(read_only=True, many=True)

    class Meta:
        """
        Мета-класс
        """

        model = ProductInfo
        fields = (
            "id",
            "model",
            "product",
            "shop",
            "quantity",
            "price",
            "price_rrc",
            "product_parameters",
        )
        read_only_fields = ("id",)
