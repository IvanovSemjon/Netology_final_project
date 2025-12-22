"""
Сериализаторы заказов.
"""

from backend.models import Order, OrderItem
from rest_framework import serializers

from .contact import ContactSerializer
from .product import ProductInfoSerializer


class OrderItemSerializer(serializers.ModelSerializer):
    """
    Сериализатор для визуализации заказа для пользователя.
    """

    class Meta:
        """
        Мета-класс.
        """

        model = OrderItem
        fields = (
            "id",
            "product_info",
            "quantity",
            "order",
        )
        read_only_fields = ("id",)
        extra_kwargs = {"order": {"write_only": True}}


class OrderItemCreateSerializer(OrderItemSerializer):
    """
    Сериализатор для визуализации продукта.
    """

    product_info = ProductInfoSerializer(read_only=True)


class OrderSerializer(serializers.ModelSerializer):
    """
    Сериализатор для визуализации заказа для магазина.
    """

    ordered_items = OrderItemCreateSerializer(read_only=True, many=True)
    total_sum = serializers.IntegerField()
    contact = ContactSerializer(read_only=True)

    class Meta:
        """
        Мета-класс.
        """

        model = Order
        fields = (
            "id",
            "ordered_items",
            "state",
            "dt",
            "total_sum",
            "contact",
        )
        read_only_fields = ("id",)
