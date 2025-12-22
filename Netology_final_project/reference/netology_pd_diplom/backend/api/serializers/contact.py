"""
Сериализаторы контактов.
"""

from backend.models import Contact
from backend.validators import validate_phone_number
from rest_framework import serializers


class ContactSerializer(serializers.ModelSerializer):
    """
    Сериализатор для информации по контакту доставки.
    """

    class Meta:
        """
        Мета-класс.
        """

        model = Contact
        fields = (
            "id",
            "city",
            "street",
            "house",
            "structure",
            "building",
            "apartment",
            "user",
            "phone",
        )
        read_only_fields = ("id",)
        extra_kwargs = {
            "user": {"write_only": True},
            "city": {"required": True},
            "street": {"required": True},
            "phone": {"required": True},
        }

    def validate_phone(self, value):
        """
        Проверка телефона.
        """
        validate_phone_number(value)
        return value

    def validate(self, data):
        """
        Проверка заполнения полей город и улица.
        """
        if not data.get("city") or not data.get("city").strip():
            raise serializers.ValidationError("Город обязателен для заполнения")
        if not data.get("street") or not data.get("street").strip():
            raise serializers.ValidationError("Улица обязательна для заполнения")
        return data
