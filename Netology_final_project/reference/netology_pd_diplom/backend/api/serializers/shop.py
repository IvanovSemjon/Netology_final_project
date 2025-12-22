"""
Сериализаторы статусов магазинов.
"""

from backend.models import Shop
from rest_framework import serializers


class ShopSerializer(serializers.ModelSerializer):
    """
    Сериализатор статуса магазина.
    """

    status_order = serializers.SerializerMethodField()

    class Meta:
        """
        Мета-класс.
        """

        model = Shop
        fields = ("id", "name", "is_accepting_orders", "status_order")
        read_only_fields = ("id",)

    def get_status_order(self, obj):
        """
        Получение статуса магазина.
        """
        return "Принимает заказы" if obj.is_accepting_orders else "Не принимает заказы"
