"""
Views заказов
"""

from backend.api.serializers import OrderSerializer
from backend.models import Order
from backend.services.emails import send_order_confirmation_email
from backend.signals import new_order
from django.db import IntegrityError
from django.db.models import F, Sum
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


class OrderView(APIView):
    """
    Получение и оформление заказов пользователем.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Получение списка заказов пользователя.
        """
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

        return Response(
            OrderSerializer(orders, many=True).data, status=status.HTTP_200_OK
        )

    def post(self, request):
        """
        Оформление заказа пользователем.
        """
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
