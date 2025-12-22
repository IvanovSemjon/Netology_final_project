"""
Сериализаторы партнеров.
"""
from rest_framework import serializers


class PartnerUpdateSerializer(serializers.Serializer):
    """
    Сериалайзер для обновления прайса для партнеров.
    """
    url = serializers.URLField(required=False, help_text="URL к YAML файлу с прайс-листом")
    file = serializers.FileField(required=False, help_text="YAML файл с прайс-листом")
    def validate(self, data):
        """
        Проверяем, что указан либо URL, либо файл.
        """
        if not data.get('url') and not data.get('file'):
            raise serializers.ValidationError("Необходимо указать URL или загрузить файл")
        return data