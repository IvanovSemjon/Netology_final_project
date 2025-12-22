"""
Сериализаторы пользователя.
"""

from backend.models import User
from backend.validators import validate_password_strength
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .contact import ContactSerializer


class UserSerializer(serializers.ModelSerializer):
    """
    Сериализатор пользователя.
    """

    contacts = ContactSerializer(read_only=True, many=True)
    password = serializers.CharField(write_only=True, required=False)
    email = serializers.EmailField(required=True)

    class Meta:
        """
        Мета-класс.
        """

        model = User
        fields = (
            "id",
            "first_name",
            "last_name",
            "email",
            "company",
            "position",
            "contacts",
            "password",
        )
        read_only_fields = ("id",)
        extra_kwargs = {
            "first_name": {"required": True},
            "last_name": {"required": True},
        }

    def validate_password(self, value):
        """
        Валидация пароля.
        """
        if value:
            validate_password(value)
            validate_password_strength(value)
        return value

    def validate_email(self, value):
        """
        Валидация email.
        """
        # Проверяем только при создании или если email изменился
        if self.instance is None:  # Создание нового пользователя
            if User.objects.filter(email=value).exists():
                raise serializers.ValidationError(
                    "Пользователь с таким email уже существует"
                )
        else:  # Обновление существующего пользователя
            if (
                value != self.instance.email
                and User.objects.filter(email=value).exists()
            ):
                raise serializers.ValidationError(
                    "Пользователь с таким email уже существует"
                )
        return value.lower()

    def create(self, validated_data):
        """
        Создание пользователя с хешированием пароля.
        """
        password = validated_data.pop("password", None)
        user = User.objects.create(**validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user
