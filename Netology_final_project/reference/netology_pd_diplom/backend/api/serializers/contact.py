from rest_framework import serializers
from backend.models import Contact
from backend.validators import validate_phone_number


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = (
            'id', 'city', 'street', 'house', 'structure',
            'building', 'apartment', 'user', 'phone'
        )
        read_only_fields = ('id',)
        extra_kwargs = {
            'user': {'write_only': True},
            'city': {'required': True},
            'street': {'required': True},
            'phone': {'required': True},
        }
    
    def validate_phone(self, value):
        """Валидация телефона"""
        validate_phone_number(value)
        return value
    
    def validate(self, data):
        """Общая валидация"""
        if not data.get('city') or not data.get('city').strip():
            raise serializers.ValidationError('Город обязателен для заполнения')
        if not data.get('street') or not data.get('street').strip():
            raise serializers.ValidationError('Улица обязательна для заполнения')
        return data