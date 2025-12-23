"""
Views для корзины заказов.
"""

from collections import defaultdict
from django.db import IntegrityError

from backend.api.serializers import OrderItemSerializer, OrderSerializer
from backend.models import Order, OrderItem, ProductInfo
from drf_spectacular.utils import OpenApiParameter
from drf_spectacular.utils import extend_schema
from django.db.models import F, Sum, Q
from rest_framework import serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


# ----------------------
# Сериализаторы для документации
# ----------------------


class BasketItemSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False)
    product_info = serializers.IntegerField()
    quantity = serializers.IntegerField()


class BasketAddRequestSerializer(serializers.Serializer):
    items = BasketItemSerializer(many=True)


class BasketAddResponseSerializer(serializers.Serializer):
    status = serializers.BooleanField()
    created_objects = serializers.IntegerField()
    message = serializers.CharField()


class BasketUpdateRequestSerializer(serializers.Serializer):
    items = BasketItemSerializer(many=True)


class BasketUpdateResponseSerializer(serializers.Serializer):
    status = serializers.BooleanField()
    updated_objects = serializers.IntegerField()


class BasketDeleteRequestSerializer(serializers.Serializer):
    items = serializers.ListField(child=serializers.IntegerField())


class BasketDeleteResponseSerializer(serializers.Serializer):
    status = serializers.BooleanField()
    deleted_objects = serializers.IntegerField()


class ErrorResponseSerializer(serializers.Serializer):
    status = serializers.BooleanField()
    errors = serializers.CharField()


# ----------------------
# View
# ----------------------


class BasketView(APIView):
    """
    Управление корзиной покупок пользователя.
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Просмотр корзины",
        description="Получение всех товаров текущей корзины пользователя",
        responses=OrderSerializer(many=True),
        tags=["Корзина"],
    )
    def get(self, request, *args, **kwargs):
        """
        Просмотр корзины.
        """
        basket = (
            Order.objects.filter(user_id=request.user.id, state="basket")
            .prefetch_related(
                "ordered_items__product_info__product__category",
                "ordered_items__product_info__product_parameters__parameter",
            )
            .annotate(
                total_sum=Sum(
                    F("ordered_items__quantity")
                    * F("ordered_items__product_info__price")
                )
            )
            .distinct()
        )
        serializer = OrderSerializer(basket, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Добавление товаров в корзину",
        description="Добавляет товары в корзину пользователя",
        request=BasketAddRequestSerializer,
        responses={201: BasketAddResponseSerializer, 400: ErrorResponseSerializer},
        tags=["Корзина"],
    )
    def post(self, request, *args, **kwargs):
        """
        Добавление товаров в корзину.
        """
        items = request.data.get("items")
        if not isinstance(items, list) or not items:
            return Response(
                {"status": False, "errors": "items должен быть непустым массивом"},
                status=400,
            )

        basket, _ = Order.objects.get_or_create(user_id=request.user.id, state="basket")
        objects_created = 0

        for order_item in items:
            order_item["order"] = basket.id
            serializer = OrderItemSerializer(data=order_item)
            if serializer.is_valid():
                try:
                    serializer.save()
                    objects_created += 1
                except IntegrityError as error:
                    return Response({"status": False, "errors": str(error)}, status=400)
            else:
                return Response(
                    {"status": False, "errors": serializer.errors}, status=400
                )

        product_ids = [item["product_info"] for item in items]
        products = ProductInfo.objects.select_related("shop").filter(id__in=product_ids)
        products_map = {p.id: p for p in products}

        shop_items = defaultdict(int)
        for item in items:
            product_info = products_map.get(item["product_info"])
            if product_info:
                shop_items[product_info.shop.name] += item["quantity"]

        message_parts = [
            f"{qty} товар{'а' if qty != 1 else ''} из магазина {shop}"
            for shop, qty in shop_items.items()
        ]
        summary = "В заказ добавлено: " + ", ".join(message_parts)

        return Response(
            {"status": True, "created_objects": objects_created, "message": summary},
            status=201,
        )



    @extend_schema(
        summary="Удаление товаров из корзины",
        description="Удаляет указанные товары из корзины по product_info",
        request=BasketDeleteRequestSerializer,
        responses={200: BasketDeleteResponseSerializer, 400: ErrorResponseSerializer},
        tags=["Корзина"],
    )
    def delete(self, request, *args, **kwargs):
        """
        Удаление товаров из корзины.
        """
        items = request.data.get("items")
        if not items:
            return Response(
                {"status": False, "errors": "Не указаны объекты для удаления"},
                status=400,
            )

        if isinstance(items, str):
            items = items.split(",")

        basket, _ = Order.objects.get_or_create(user_id=request.user.id, state="basket")
        deleted_count = OrderItem.objects.filter(order=basket, product_info_id__in=items).delete()[0]

        if deleted_count > 0:
            return Response({"status": True, "deleted_objects": deleted_count})

        return Response(
            {"status": False, "errors": "Нет корректных объектов для удаления"},
            status=400,
        )


    @extend_schema(
        summary="Обновление количества товаров в корзине",
        description="Обновляет количество товаров в корзине",
        request=BasketUpdateRequestSerializer,
        responses={200: BasketUpdateResponseSerializer, 400: ErrorResponseSerializer},
        tags=["Корзина"],
    )
    def put(self, request, *args, **kwargs):
        """
        Изменение количества товаров в корзине.
        """
        items = request.data.get("items")
        if not isinstance(items, list) or not items:
            return Response(
                {"status": False, "errors": "items должен быть непустым массивом"},
                status=400,
            )

        basket, _ = Order.objects.get_or_create(user_id=request.user.id, state="basket")
        objects_updated = 0

        for item in items:
            item_id = item.get("id")
            quantity = item.get("quantity")
            if isinstance(item_id, int) and isinstance(quantity, int):
                objects_updated += OrderItem.objects.filter(
                    order=basket, id=item_id
                ).update(quantity=quantity)

        return Response({"status": True, "updated_objects": objects_updated})
