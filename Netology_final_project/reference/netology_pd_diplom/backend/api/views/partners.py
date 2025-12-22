"""
Views по партнерам.
"""
import yaml
from backend.api.serializers import OrderSerializer, ShopSerializer
from backend.api.serializers.partners import PartnerUpdateSerializer
from backend.models import (
    Category, Order, OrderStatusHistory, Parameter, Product, ProductInfo, ProductParameter, Shop
)
from backend.utils import strtobool
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.db.models import F, Sum
from requests import get
from rest_framework import status, serializers
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema


# ----------------------
# Сериализаторы для документации
# ----------------------

class PartnerUpdateRequestSerializer(serializers.Serializer):
    file = serializers.FileField(required=False)
    url = serializers.URLField(required=False)


class PartnerUpdateResponseSerializer(serializers.Serializer):
    status = serializers.BooleanField()
    message = serializers.CharField()
    errors = serializers.ListField(child=serializers.CharField(), required=False)


class PartnerStateResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    is_accepting_orders = serializers.BooleanField()


class PartnerStateUpdateRequestSerializer(serializers.Serializer):
    state = serializers.CharField()


class PartnerOrdersResponseSerializer(serializers.Serializer):
    # Используем OrderSerializer для списка заказов
    orders = OrderSerializer(many=True)


class PartnerOrderStatusUpdateRequestSerializer(serializers.Serializer):
    order_id = serializers.IntegerField()
    status = serializers.ChoiceField(choices=["confirmed", "assembled", "sent", "delivered"])


class PartnerOrderStatusUpdateResponseSerializer(serializers.Serializer):
    status = serializers.BooleanField()
    message = serializers.CharField()
    errors = serializers.CharField(required=False)


# ----------------------
# Views
# ----------------------

class PartnerUpdate(APIView):
    """
    Обновление информации о партнёрах (прайс-лист).
    """

    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_serializer(self, *args, **kwargs):
        return PartnerUpdateSerializer(*args, **kwargs)

    @extend_schema(
        summary="Обновление прайса партнёра",
        description="Позволяет загружать файл или указать URL с прайс-листом для магазина",
        request=PartnerUpdateRequestSerializer,
        responses={200: PartnerUpdateResponseSerializer, 400: PartnerUpdateResponseSerializer},
        tags=["Партнёры"]
    )
    def post(self, request, *args, **kwargs):
        if request.user.type != "shop":
            return Response({"status": False, "errors": "Только для магазинов"}, status=status.HTTP_403_FORBIDDEN)

        file = request.FILES.get("file")
        url = request.data.get("url")

        if file:
            try:
                stream = file.read()
                data = yaml.safe_load(stream)
            except Exception as e:
                return Response({"status": False, "errors": [f"Ошибка чтения файла: {str(e)}"]}, status=400)
        elif url:
            validate_url = URLValidator()
            try:
                validate_url(url)
            except ValidationError as e:
                return Response({"status": False, "errors": [str(e)]}, status=400)
            else:
                response = get(url, timeout=10)
                response.raise_for_status()
                stream = response.content
                data = yaml.safe_load(stream)
        else:
            return Response({"status": False, "errors": ["Необходимо указать URL или загрузить файл"]}, status=400)

        try:
            shop, _ = Shop.objects.get_or_create(user_id=request.user.id, defaults={"name": data.get("shop", f"Магазин {request.user.email}")})

            if "categories" in data:
                for category in data["categories"]:
                    category_object, _ = Category.objects.get_or_create(id=category.get("id"), name=category.get("name"))
                    category_object.shops.add(shop.id)
                    category_object.save()

            ProductInfo.objects.filter(shop_id=shop.id).delete()
            created_count = 0
            errors = []

            if "goods" in data and data["goods"]:
                for item in data["goods"]:
                    try:
                        product, _ = Product.objects.get_or_create(
                            name=item.get("name", "Неизвестный товар"),
                            category_id=item.get("category"),
                        )
                        product_info = ProductInfo.objects.create(
                            product_id=product.id,
                            external_id=item.get("id"),
                            model=item.get("model", ""),
                            price=item.get("price", 0),
                            price_rrc=item.get("price_rrc", 0),
                            quantity=item.get("quantity", 0),
                            shop_id=shop.id,
                        )

                        if "parameters" in item:
                            for name, value in item["parameters"].items():
                                parameter_object, _ = Parameter.objects.get_or_create(name=name)
                                ProductParameter.objects.create(
                                    product_info_id=product_info.id,
                                    parameter_id=parameter_object.id,
                                    value=value,
                                )
                        created_count += 1
                    except Exception as e:
                        errors.append(f"Ошибка при создании товара {item.get('name')}: {str(e)}")
        except Exception as e:
            return Response({"status": False, "errors": [f"Ошибка обработки данных: {str(e)}"]}, status=400)

        response_data = {"status": True, "message": f"Прайс-лист успешно изменен. Обновлено {created_count} товаров"}
        if errors:
            response_data["errors"] = errors[:5]
        return Response(response_data, status=200)


class PartnerState(APIView):
    """
    Управление состоянием партнёра.
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Получение состояния партнёра",
        description="Возвращает данные магазина",
        responses={200: PartnerStateResponseSerializer, 403: PartnerUpdateResponseSerializer},
        tags=["Партнёры"]
    )
    def get(self, request, *args, **kwargs):
        if request.user.type != "shop":
            return Response({"status": False, "errors": "Только для магазинов"}, status=403)
        try:
            shop = Shop.objects.get(user_id=request.user.id)
        except Shop.DoesNotExist:
            return Response({"status": False, "errors": "Магазин не найден"}, status=404)
        serializer = ShopSerializer(shop)
        return Response(serializer.data, status=200)

    @extend_schema(
        summary="Обновление состояния партнёра",
        description="Обновляет статус магазина (принимает заказы или нет)",
        request=PartnerStateUpdateRequestSerializer,
        responses={200: PartnerUpdateResponseSerializer, 400: PartnerUpdateResponseSerializer},
        tags=["Партнёры"]
    )
    def post(self, request, *args, **kwargs):
        if request.user.type != "shop":
            return Response({"status": False, "errors": "Только для магазинов"}, status=403)
        state = request.data.get("state")
        if state:
            try:
                Shop.objects.filter(user_id=request.user.id).update(is_accepting_orders=strtobool(state))
                return Response({"status": True, "message": "Статус магазина успешно изменен"}, status=200)
            except ValueError as error:
                return Response({"status": False, "errors": str(error)}, status=400)
        return Response({"status": False, "errors": "Не указаны все необходимые аргументы"}, status=400)


class PartnerOrders(APIView):
    """
    Управление заказами партнёра.
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Получение заказов магазина",
        description="Возвращает список заказов, связанных с магазином",
        responses={200: OrderSerializer(many=True), 403: PartnerUpdateResponseSerializer},
        tags=["Партнёры"]
    )
    def get(self, request, *args, **kwargs):
        if request.user.type != "shop":
            return Response({"status": False, "errors": "Только для магазинов"}, status=403)
        orders = (
            Order.objects.filter(ordered_items__product_info__shop__user_id=request.user.id)
            .exclude(state="basket")
            .prefetch_related(
                "ordered_items__product_info__product__category",
                "ordered_items__product_info__product_parameters__parameter",
            )
            .select_related("contact")
            .annotate(total_sum=Sum(F("ordered_items__quantity") * F("ordered_items__product_info__price")))
            .distinct()
        )
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data, status=200)

    @extend_schema(
        summary="Обновление статуса заказа",
        description="Позволяет магазину изменить статус заказа",
        request=PartnerOrderStatusUpdateRequestSerializer,
        responses={200: PartnerOrderStatusUpdateResponseSerializer, 400: PartnerOrderStatusUpdateResponseSerializer},
        tags=["Партнёры"]
    )
    def post(self, request, *args, **kwargs):
        if request.user.type != "shop":
            return Response({"status": False, "errors": "Только для магазинов"}, status=403)
        if {"order_id", "status"}.issubset(request.data):
            order_id = request.data["order_id"]
            new_status = request.data["status"]
            allowed_statuses = ["confirmed", "assembled", "sent", "delivered"]
            if new_status not in allowed_statuses:
                return Response({"status": False, "errors": f'Недопустимый статус. Разрешены: {", ".join(allowed_statuses)}'}, status=400)
            try:
                order = Order.objects.filter(id=order_id, ordered_items__product_info__shop__user_id=request.user.id).first()
                if not order:
                    return Response({"status": False, "errors": "Заказ не найден"}, status=404)
                old_status = order.state
                order.state = new_status
                order.save()
                OrderStatusHistory.objects.create(
                    order=order,
                    old_status=old_status,
                    new_status=new_status,
                    changed_by=request.user,
                    comment=f"Статус изменен магазином {request.user.email}",
                )
                status_names = {"confirmed": "Подтвержден", "assembled": "Собран", "sent": "Отправлен", "delivered": "Доставлен"}
                return Response({"status": True, "message": f'Статус заказа #{order_id} изменен на "{status_names.get(new_status, new_status)}"'}, status=200)
            except Exception as e:
                return Response({"status": False, "errors": f"Ошибка: {str(e)}"}, status=400)
        return Response({"status": False, "errors": "Не указаны все необходимые аргументы (order_id, status)"}, status=400)