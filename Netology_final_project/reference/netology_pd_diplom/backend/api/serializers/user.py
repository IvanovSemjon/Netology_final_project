"""
Сериализаторы пользователя.
"""

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from dj_rest_auth.registration.serializers import RegisterSerializer
from rest_framework import serializers
from allauth.account.adapter import get_adapter
from allauth.account.utils import setup_user_email

from backend.validators import validate_password_strength
from .contact import ContactSerializer

# Получаем модель User
User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """
    Сериализатор пользователя.
    """

    contacts = ContactSerializer(read_only=True, many=True)
    password = serializers.CharField(write_only=True, required=False)
    email = serializers.EmailField(required=True)
    type = serializers.ChoiceField(choices=User.USER_TYPE_CHOICES)

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
            "type",
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

        if self.instance is None:
            if User.objects.filter(email=value).exists():
                raise serializers.ValidationError(
                    "Пользователь с таким email уже существует"
                )
        else:
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


class CustomRegisterSerializer(RegisterSerializer):
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    company = serializers.CharField(required=False, allow_blank=True)
    position = serializers.CharField(required=False, allow_blank=True)
    type = serializers.ChoiceField(choices=User.USER_TYPE_CHOICES, default='buyer')
    
    def get_cleaned_data(self):
        return {
            'username': self.validated_data.get('username', ''),
            'password1': self.validated_data.get('password1', ''),
            'password2': self.validated_data.get('password2', ''),
            'email': self.validated_data.get('email', ''),
            'first_name': self.validated_data.get('first_name', ''),
            'last_name': self.validated_data.get('last_name', ''),
            'company': self.validated_data.get('company', ''),
            'position': self.validated_data.get('position', ''),
            'type': self.validated_data.get('type', 'buyer'),
        }
    
    def save(self, request):
        adapter = get_adapter()
        user = adapter.new_user(request)
        self.cleaned_data = self.get_cleaned_data()
        adapter.save_user(request, user, self)
        
        # Сохраняем дополнительные поля
        if 'company' in self.cleaned_data:
            user.company = self.cleaned_data['company']
        if 'position' in self.cleaned_data:
            user.position = self.cleaned_data['position']
        if 'type' in self.cleaned_data:
            user.type = self.cleaned_data['type']
        
        # Для социальной регистрации активируем пользователя
        if not user.is_active:
            user.is_active = True
        
        user.save()
        
        self.custom_signup(request, user)
        setup_user_email(request, user, [])
        return user


class UserDetailsSerializer(serializers.ModelSerializer):
    contacts = ContactSerializer(read_only=True, many=True)
    
    class Meta:
        model = User
        fields = (
            'id', 
            'email', 
            'first_name', 
            'last_name', 
            'company', 
            'position',
            'type',
            'is_active',
            'contacts'
        )
        read_only_fields = ('email', 'is_active')