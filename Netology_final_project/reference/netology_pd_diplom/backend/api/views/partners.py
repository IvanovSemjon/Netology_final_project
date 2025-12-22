"""
Views по партнерам.
"""

import yaml
from backend.api.serializers import OrderSerializer, ShopSerializer
from backend.api.serializers.partners import PartnerUpdateSerializer
from backend.models import (
    Category,
    Order,
    OrderStatusHistory,
    Parameter,
    Product,
    ProductInfo,
    ProductParameter,
    Shop,
)
from backend.utils import strtobool
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.db.models import F, Sum
from requests import get
from rest_framework import status
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


class PartnerUpdate(APIView):
    """
    Обновление информации о партнерах.
    """

    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    serializer_class = PartnerUpdateSerializer

    def get_serializer(self, *args, **kwargs):
        """
        Получить сериалайзер.
        """
        return PartnerUpdateSerializer(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        """
        Обновление прайса.
        """
        if request.user.type != "shop":
            return Response(
                {"status": False, "errors": "Только для магазинов"},
                status=status.HTTP_403_FORBIDDEN,
            )

        file = request.FILES.get("file")
        url = request.data.get("url")

        if file:
            try:
                stream = file.read()
                data = yaml.safe_load(stream)
            except Exception as e:
                return Response(
                    {"status": False, "errors": f"Ошибка чтения файла: {str(e)}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        elif url:
            validate_url = URLValidator()
            try:
                validate_url(url)
            except ValidationError as e:
                return Response(
                    {"status": False, "errors": str(e)},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            else:
                response = get(url, timeout=10)
                response.raise_for_status()
                stream = response.content
                print(f"Загружено {len(stream)} байт")
                print(f"Первые 200 символов: {stream[:200]}")
                print(f"Последние 200 символов: {stream[-200:]}")
                data = yaml.safe_load(stream)

        else:
            return Response(
                {
                    "status": False,
                    "errors": "Необходимо указать URL или загрузить файл",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            try:
                shop = Shop.objects.get(user_id=request.user.id)
            except Shop.DoesNotExist:
                shop_name = data.get("shop", f"Магазин {request.user.email}")
                shop = Shop.objects.create(name=shop_name, user_id=request.user.id)

            if "categories" in data:
                for category in data["categories"]:
                    category_object, _ = Category.objects.get_or_create(
                        id=category.get("id"), name=category.get("name")
                    )
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
                                parameter_object, _ = Parameter.objects.get_or_create(
                                    name=name
                                )
                                ProductParameter.objects.create(
                                    product_info_id=product_info.id,
                                    parameter_id=parameter_object.id,
                                    value=value,
                                )
                        created_count += 1
                    except Exception as e:
                        error_msg = (
                            f"Ошибка при создании товара {item.get('name')}: {str(e)}"
                        )
                        errors.append(error_msg)
                        continue
        except Exception as e:
            return Response(
                {"status": False, "errors": f"Ошибка обработки данных: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        response_data = {
            "status": True,
            "message": f"Прайс-лист успешно изменен. Обновлено {created_count} товаров",
        }
        if errors:
            response_data["errors"] = errors[:5]
        return Response(response_data, status=status.HTTP_200_OK)


class PartnerState(APIView):
    """
    Управление состоянием партнера.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """
        Получить информацию о состоянии партнера.
        """
        if request.user.type != "shop":
            return Response(
                {"status": False, "errors": "Только для магазинов"},
                status=status.HTTP_403_FORBIDDEN,
            )
        try:
            shop = Shop.objects.get(user_id=request.user.id)
        except Shop.DoesNotExist:
            return Response(
                {"status": False, "errors": "Магазин не найден"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ShopSerializer(shop)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        """
        Обновить информацию о состоянии партнера.
        """
        if request.user.type != "shop":
            return Response(
                {"status": False, "error": "Только для магазинов"},
                status=status.HTTP_403_FORBIDDEN,
            )

        state = request.data.get("state")
        if state:
            try:
                Shop.objects.filter(user_id=request.user.id).update(
                    is_accepting_orders=strtobool(state)
                )
                return Response(
                    {"status": True, "message": "Статус магазина успешно изменен"},
                    status=status.HTTP_200_OK,
                )
            except ValueError as error:
                return Response(
                    {"status": False, "errors": str(error)},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        return Response(
            {"status": False, "errors": "Не указаны все необходимые аргументы"},
            status=status.HTTP_400_BAD_REQUEST,
        )


class PartnerOrders(APIView):
    """
    Класс для получения заказов поставщиками.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """
        Получение заказов для магазинов.
        """

        if request.user.type != "shop":
            return Response(
                {"status": False, "errors": "Только для магазинов"},
                status=status.HTTP_403_FORBIDDEN,
            )

        order = (
            Order.objects.filter(
                ordered_items__product_info__shop__user_id=request.user.id
            )
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

        serializer = OrderSerializer(order, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        """
        Изменить статус заказа магазином.
        """
        if request.user.type != "shop":
            return Response(
                {"status": False, "errors": "Только для магазинов"},
                status=status.HTTP_403_FORBIDDEN,
            )

        if {"order_id", "status"}.issubset(request.data):
            order_id = request.data["order_id"]
            new_status = request.data["status"]

            allowed_statuses = ["confirmed", "assembled", "sent", "delivered"]
            if new_status not in allowed_statuses:
                return Response(
                    {
                        "status": False,
                        "errors": f'Недопустимый статус. Разрешены: {", ".join(allowed_statuses)}',
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            try:
                order = Order.objects.filter(
                    id=order_id,
                    ordered_items__product_info__shop__user_id=request.user.id,
                ).first()

                if not order:
                    return Response(
                        {"status": False, "errors": "Заказ не найден"},
                        status=status.HTTP_404_NOT_FOUND,
                    )

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

                status_names = {
                    "confirmed": "Подтвержден",
                    "assembled": "Собран",
                    "sent": "Отправлен",
                    "delivered": "Доставлен",
                }

                return Response(
                    {
                        "status": True,
                        "message": f'Статус заказа #{order_id} изменен на "{status_names.get(new_status, new_status)}"',
                    },
                    status=status.HTTP_200_OK,
                )

            except Exception as e:
                return Response(
                    {"status": False, "errors": f"Ошибка: {str(e)}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        return Response(
            {
                "status": False,
                "errors": "Не указаны все необходимые аргументы (order_id, status)",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )
