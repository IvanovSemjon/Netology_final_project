"""
Views для каталога товаров.
"""

from backend.api.serializers import (CategorySerializer, ProductInfoSerializer,
                                     ShopSerializer)
from backend.models import Category, ProductInfo, Shop
from django.db.models import Q
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView


class CategoryView(ListAPIView):
    """
    Класс для просмотра категорий.
    """

    permission_classes = [AllowAny]
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ShopView(ListAPIView):
    """
    Класс для просмотра списка магазинов.
    """

    permission_classes = [AllowAny]
    queryset = Shop.objects.filter(is_accepting_orders=True)
    serializer_class = ShopSerializer


class ProductInfoView(APIView):
    """
    Поиск продуктов.
    """

    permission_classes = [AllowAny]

    def get(self, request: Request, *args, **kwargs):
        """
        Получить информацию о товаре по фильтрам.
        """
        query = Q(shop__is_accepting_orders=True)
        shop_id = request.query_params.get("shop_id")
        category_id = request.query_params.get("category_id")

        if shop_id:
            query = query & Q(shop_id=shop_id)

        if category_id:
            query = query & Q(product__category_id=category_id)

        queryset = (
            ProductInfo.objects.filter(query)
            .select_related("shop", "product__category")
            .prefetch_related("product_parameters__parameter")
            .distinct()
        )

        serializer = ProductInfoSerializer(queryset, many=True)

        return Response(serializer.data)
