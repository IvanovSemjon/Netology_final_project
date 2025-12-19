from django.db import IntegrityError
from django.db.models import Q, Sum, F
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework.views import APIView
from ujson import loads as load_json

from backend.models import Order, OrderItem
from backend.api.serializers import OrderItemSerializer, OrderSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny


class BasketView(APIView):
    """
    Управление корзиной покупок пользователя
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """
        Получить список товаров в корзине
        """
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)
        
        basket = Order.objects.filter(
            user_id=request.user.id, state='basket').prefetch_related(
            'ordered_items__product_info__product__category',
            'ordered_items__product_info__product_parameters__parameter').annotate(
            total_sum=Sum(F('ordered_items__quantity') * F('ordered_items__product_info__price'))).distinct()

        serializer = OrderSerializer(basket, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        """
        Добавить товары в корзину
        """
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)

        items_string = request.data.get('items')
        if items_string:
            try:
                items_dict = load_json(items_string)
            except ValueError:
                return JsonResponse({'Status': False, 'Errors': 'Неверный формат запроса'})
            else:
                basket, _ = Order.objects.get_or_create(user_id=request.user.id, state='basket')
                objects_created = 0
                for order_item in items_dict:
                    order_item.update({'order': basket.id})
                    serializer = OrderItemSerializer(data=order_item)
                    if serializer.is_valid():
                        try:
                            serializer.save()
                        except IntegrityError as error:
                            return JsonResponse({'Status': False, 'Errors': str(error)})
                        else:
                            objects_created += 1
                    else:
                        return JsonResponse({'Status': False, 'Errors': serializer.errors})

                # Подсчитываем товары по магазинам
                from collections import defaultdict
                shop_items = defaultdict(int)
                for order_item in items_dict:
                    from backend.models import ProductInfo
                    try:
                        product_info = ProductInfo.objects.select_related('shop').get(id=order_item['product_info'])
                        shop_items[product_info.shop.name] += order_item['quantity']
                    except ProductInfo.DoesNotExist:
                        pass
                
                # Формируем сообщение
                message_parts = []
                for shop_name, quantity in shop_items.items():
                    if quantity == 1:
                        message_parts.append(f"1 товар из магазина {shop_name}")
                    else:
                        message_parts.append(f"{quantity} товара из магазина {shop_name}")
                
                summary = "В заказ добавлено: " + ", ".join(message_parts)
                
                return JsonResponse({
                    'Status': True, 
                    'Создано объектов': objects_created,
                    'Message': summary
                })
        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})

    def delete(self, request, *args, **kwargs):
        """
        Удалить товары из корзины
        """
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)

        items_string = request.data.get('items')
        if items_string:
            items_list = items_string.split(',')
            basket, _ = Order.objects.get_or_create(user_id=request.user.id, state='basket')
            query = Q()
            objects_deleted = False
            for order_item_id in items_list:
                if order_item_id.isdigit():
                    query = query | Q(order_id=basket.id, id=order_item_id)
                    objects_deleted = True

            if objects_deleted:
                deleted_count = OrderItem.objects.filter(query).delete()[0]
                return JsonResponse({'Status': True, 'Удалено объектов': deleted_count})
        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})

    def put(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)

        items = request.data.get('items')

        if not isinstance(items, list):
            return JsonResponse({'Status': False, 'Errors': 'items должен быть массивом'}, status=400)

        basket, _ = Order.objects.get_or_create(
            user_id=request.user.id,
            state='basket'
        )

        objects_updated = 0

        for item in items:
            item_id = item.get('id')
            quantity = item.get('quantity')

            if not isinstance(item_id, int) or not isinstance(quantity, int):
                continue

            objects_updated += OrderItem.objects.filter(
                order=basket,
                id=item_id
            ).update(quantity=quantity)

        return JsonResponse({
            'Status': True,
            'Обновлено объектов': objects_updated
        })
