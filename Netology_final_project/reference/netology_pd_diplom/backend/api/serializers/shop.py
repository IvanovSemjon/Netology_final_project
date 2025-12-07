from rest_framework import serializers
from backend.models import Shop


class ShopSerializer(serializers.ModelSerializer):
    статус_заказов = serializers.SerializerMethodField()
    
    class Meta:
        model = Shop
        fields = ('id', 'name', 'is_accepting_orders', 'статус_заказов')
        read_only_fields = ('id',)
    
    def get_статус_заказов(self, obj):
        return "Принимает заказы" if obj.is_accepting_orders else "Не принимает заказы"