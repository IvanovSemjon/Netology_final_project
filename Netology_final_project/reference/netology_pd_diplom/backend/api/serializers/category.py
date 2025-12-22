"""
Сериализаторы категорий.
"""

from backend.models import Category
from rest_framework import serializers


class CategorySerializer(serializers.ModelSerializer):
    """
    Сериализатор категории.
    """
    class Meta:
        """
        Мета-класс.
        """

        model = Category
        fields = (
            "id",
            "name",
        )
        read_only_fields = ("id",)
