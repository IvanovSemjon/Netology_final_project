"""
Views заказов
"""

from backend.api.serializers import OrderSerializer
from backend.models import Order
from backend.services.emails import send_order_confirmation_email
from backend.signals import new_order
from django.db import IntegrityError
from django.db.models import F, Sum
from rest_framework import serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema


class OrderListResponseSerializer(serializers.ModelSerializer):
    total_sum = serializers.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        model = Order
        fields = "__all__"


class OrderCreateRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    contact = serializers.IntegerField()


class OrderCreateResponseSerializer(serializers.Serializer):
    status = serializers.BooleanField()
    message = serializers.CharField()


class ErrorResponseSerializer(serializers.Serializer):
    status = serializers.BooleanField()
    errors = serializers.CharField()


class OrderView(APIView):
    """
    Получение и оформление заказов пользователем.
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Получение заказов пользователя",
        description="Возвращает список всех заказов пользователя, кроме корзины",
        responses=OrderListResponseSerializer(many=True),
        tags=["Заказы"]
    )
    def get(self, request):
        new_order.send(sender=self.__class__, user_id=request.user.id)
        orders = (
            Order.objects.filter(user_id=request.user.id)
            .exclude(state="basket")
            .prefetch_related(
                "ordered_items__product_info__product__category",
                "ordered_items__product_info__product_parameters__parameter",
            )
            .select_related("contact")
            .annotate(
                total_sum=Sum(
                    F("ordered_items__quantity")
                    * F("ordered_items__product_info__price")
                )
            )
            .distinct()
        )

        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Оформление заказа",
        description="Позволяет оформить заказ из корзины, указывая контакт",
        request=OrderCreateRequestSerializer,
        responses={200: OrderCreateResponseSerializer, 400: ErrorResponseSerializer},
        tags=["Заказы"]
    )
    def post(self, request):
        if {"id", "contact"}.issubset(request.data):
            order_id = request.data["id"]

            if str(order_id).isdigit():
                try:
                    updated = Order.objects.filter(
                        id=order_id, user_id=request.user.id, state="basket"
                    ).update(contact_id=request.data["contact"], state="new")
                except IntegrityError:
                    return Response(
                        {"status": False, "errors": "Неправильные аргументы"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                if updated:
                    order = Order.objects.get(id=order_id)
                    new_order.send(sender=self.__class__, user_id=request.user.id)
                    send_order_confirmation_email(order)

                    return Response(
                        {"status": True, "message": "Заказ подтверждён"},
                        status=status.HTTP_200_OK,
                    )

        return Response(
            {"status": False, "errors": "Не указаны все необходимые аргументы"},
            status=status.HTTP_400_BAD_REQUEST,
        )