"""
Views для каталога товаров.
"""

from backend.api.serializers import CategorySerializer, ProductInfoSerializer, ShopSerializer
from backend.models import Category, ProductInfo, Shop
from django.db.models import Q
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import serializers
from drf_spectacular.utils import extend_schema, OpenApiParameter



class CategoryView(ListAPIView):
    """
    Просмотр категорий.
    """
    permission_classes = [AllowAny]
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    @extend_schema(
        summary="Список категорий",
        description="Возвращает список всех категорий продуктов.",
        tags=['Каталог']
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class ShopView(ListAPIView):
    """
    Просмотр магазинов, которые принимают заказы.
    """
    permission_classes = [AllowAny]
    queryset = Shop.objects.filter(is_accepting_orders=True)
    serializer_class = ShopSerializer

    @extend_schema(
        summary="Список магазинов",
        description="Возвращает список магазинов, которые принимают заказы.",
        tags=['Каталог']
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class ProductInfoQuerySerializer(serializers.Serializer):
    shop_id = serializers.IntegerField(required=False, help_text="ID магазина для фильтрации")
    category_id = serializers.IntegerField(required=False, help_text="ID категории для фильтрации")


class ProductInfoView(APIView):
    """
    Поиск и фильтрация продуктов.
    """
    permission_classes = [AllowAny]

    @extend_schema(
        summary="Список продуктов",
        description="Возвращает список продуктов с фильтрацией по магазину и категории.",
        parameters=[
            OpenApiParameter(name='shop_id', type=int, description='ID магазина', required=False),
            OpenApiParameter(name='category_id', type=int, description='ID категории', required=False),
        ],
        responses=ProductInfoSerializer(many=True),
        tags=['Каталог']
    )
    def get(self, request: Request, *args, **kwargs):
        query = Q(shop__is_accepting_orders=True)
        shop_id = request.query_params.get("shop_id")
        category_id = request.query_params.get("category_id")

        if shop_id:
            query &= Q(shop_id=shop_id)

        if category_id:
            query &= Q(product__category_id=category_id)

        queryset = (
            ProductInfo.objects.filter(query)
            .select_related("shop", "product__category")
            .prefetch_related("product_parameters__parameter")
            .distinct()
        )

        serializer = ProductInfoSerializer(queryset, many=True)
        return Response(serializer.data)