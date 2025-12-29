"""
Views для корзины заказов.
"""

from collections import defaultdict

from django.db import IntegrityError
from django.db.models import F, Sum
from rest_framework import serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle, UserRateThrottle
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema

from backend.models import Order, OrderItem, ProductInfo
from backend.api.serializers import OrderSerializer


class BasketItemWriteSerializer(serializers.Serializer):
    product_info = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)


class BasketAddRequestSerializer(serializers.Serializer):
    items = BasketItemWriteSerializer(many=True)


class BasketAddResponseSerializer(serializers.Serializer):
    status = serializers.BooleanField()
    created_objects = serializers.IntegerField()
    message = serializers.CharField()


class BasketUpdateItemSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)


class BasketUpdateRequestSerializer(serializers.Serializer):
    items = BasketUpdateItemSerializer(many=True)


class BasketUpdateResponseSerializer(serializers.Serializer):
    status = serializers.BooleanField()
    updated_objects = serializers.IntegerField()


class BasketDeleteRequestSerializer(serializers.Serializer):
    items = serializers.ListField(
        child=serializers.IntegerField(),
        help_text="Список product_info id"
    )


class BasketDeleteResponseSerializer(serializers.Serializer):
    status = serializers.BooleanField()
    deleted_objects = serializers.IntegerField()


class ErrorResponseSerializer(serializers.Serializer):
    status = serializers.BooleanField()
    errors = serializers.CharField()


class BasketView(APIView):
    """
    Управление корзиной покупок пользователя.
    """

    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle, ScopedRateThrottle]
    throttle_scope = "basket"

    # ---------- GET ----------
    @extend_schema(
        summary="Просмотр корзины",
        description="Получение текущей корзины пользователя",
        responses=OrderSerializer(many=True),
        tags=["Корзина"],
    )
    def get(self, request):
        basket = (
            Order.objects.filter(user=request.user, state="basket")
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

    # ---------- POST ----------
    @extend_schema(
        summary="Добавление товаров в корзину",
        request=BasketAddRequestSerializer,
        responses={201: BasketAddResponseSerializer, 400: ErrorResponseSerializer},
        tags=["Корзина"],
    )
    def post(self, request):
        serializer = BasketItemWriteSerializer(
            data=request.data.get("items"),
            many=True
        )
        serializer.is_valid(raise_exception=True)

        basket, _ = Order.objects.get_or_create(
            user=request.user,
            state="basket"
        )

        created = 0
        shop_summary = defaultdict(int)

        product_ids = [i["product_info"] for i in serializer.validated_data]
        products = ProductInfo.objects.select_related("shop").filter(id__in=product_ids)
        products_map = {p.id: p for p in products}

        try:
            for item in serializer.validated_data:
                product = products_map.get(item["product_info"])
                if not product:
                    continue

                OrderItem.objects.create(
                    order=basket,
                    product_info=product,
                    quantity=item["quantity"],
                )

                created += 1
                shop_summary[product.shop.name] += item["quantity"]

        except IntegrityError as e:
            return Response(
                {"status": False, "errors": str(e)},
                status=400
            )

        message = ", ".join(
            f"{qty} товар(ов) из магазина {shop}"
            for shop, qty in shop_summary.items()
        )

        return Response(
            {
                "status": True,
                "created_objects": created,
                "message": f"Добавлено в корзину: {message}",
            },
            status=201,
        )

    # ---------- PUT ----------
    @extend_schema(
        summary="Изменение количества товаров",
        request=BasketUpdateRequestSerializer,
        responses={200: BasketUpdateResponseSerializer},
        tags=["Корзина"],
    )
    def put(self, request):
        items = request.data.get("items", [])
        updated = 0

        basket, _ = Order.objects.get_or_create(
            user=request.user,
            state="basket"
        )

        for item in items:
            updated += OrderItem.objects.filter(
                order=basket,
                id=item["id"]
            ).update(quantity=item["quantity"])

        return Response(
            {"status": True, "updated_objects": updated}
        )

    # ---------- DELETE ----------
    @extend_schema(
        summary="Удаление товаров из корзины",
        request=BasketDeleteRequestSerializer,
        responses={200: BasketDeleteResponseSerializer},
        tags=["Корзина"],
    )
    def delete(self, request):
        product_ids = request.data.get("items", [])

        if not product_ids:
            return Response(
                {"status": False, "errors": "items не может быть пустым"},
                status=400
            )

        basket, _ = Order.objects.get_or_create(
            user=request.user,
            state="basket"
        )

        deleted, _ = OrderItem.objects.filter(
            order=basket,
            product_info_id__in=product_ids
        ).delete()

        return Response(
            {"status": True, "deleted_objects": deleted}
        )