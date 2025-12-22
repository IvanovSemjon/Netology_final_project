"""
Views для корзины заказов.
"""

from collections import defaultdict

from backend.api.serializers import OrderItemSerializer, OrderSerializer
from backend.models import Order, OrderItem, ProductInfo
from django.db import IntegrityError
from django.db.models import F, Q, Sum
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


class BasketView(APIView):
    """
    Управление корзиной покупок пользователя.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """
        Получить список товаров в корзине.
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
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        """
        Добавить товары в корзину.
        """
        items = request.data.get("items")
        if not isinstance(items, list) or not items:
            return Response(
                {"status": False, "errors": "items должен быть непустым массивом"},
                status=status.HTTP_400_BAD_REQUEST,
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
                    return Response(
                        {"status": False, "errors": str(error)},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            else:
                return Response(
                    {"status": False, "errors": serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        # Подсчёт товаров по магазинам (без N+1)
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
            {
                "status": True,
                "created_objects": objects_created,
                "message": summary,
            },
            status=status.HTTP_201_CREATED,
        )

    def delete(self, request, *args, **kwargs):
        """
        Удалить товары из корзины.
        """
        items = request.data.get("items")
        if not items:
            return Response(
                {"status": False, "errors": "Не указаны объекты для удаления"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if isinstance(items, str):
            items = items.split(",")

        basket, _ = Order.objects.get_or_create(user_id=request.user.id, state="basket")
        query = Q()
        has_items = False

        for order_item_id in items:
            if str(order_item_id).isdigit():
                query |= Q(order_id=basket.id, id=int(order_item_id))
                has_items = True

        if has_items:
            deleted_count = OrderItem.objects.filter(query).delete()[0]
            return Response({"status": True, "deleted_objects": deleted_count})

        return Response(
            {"status": False, "errors": "Нет корректных объектов для удаления"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def put(self, request, *args, **kwargs):
        """
        Корректировка количества товаров в корзине.
        """
        items = request.data.get("items")
        if not isinstance(items, list) or not items:
            return Response(
                {"status": False, "errors": "items должен быть непустым массивом"},
                status=status.HTTP_400_BAD_REQUEST,
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
