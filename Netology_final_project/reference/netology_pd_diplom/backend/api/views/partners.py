import yaml
from yaml import Loader as YamlLoader
from requests import get
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.db.models import Sum, F
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from backend.models import Shop, Category, Product, ProductInfo, Parameter, ProductParameter, Order
from backend.api.serializers import ShopSerializer, OrderSerializer
from backend.api.serializers.partners import PartnerUpdateSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from backend.utils import strtobool
from backend.constants import ERROR_MESSAGES


class PartnerUpdate(APIView):
    """
    Обновление информации о партнерах
    """
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    serializer_class = PartnerUpdateSerializer
    
    def get_serializer(self, *args, **kwargs):
        return PartnerUpdateSerializer(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        """
        Обновление прайса.
        """
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)

        if request.user.type != 'shop':
            return JsonResponse({'Status': False, 'Error': 'Только для магазинов'}, status=403)

        # Проверяем наличие файла
        file = request.FILES.get('file')
        url = request.data.get('url')
        
        if file:
            # Загрузка из файла
            try:
                stream = file.read()
                data = yaml.load(stream, Loader=YamlLoader)
            except Exception as e:
                return JsonResponse({'Status': False, 'Error': f'Ошибка чтения файла: {str(e)}'})
        elif url:
            # Загрузка по URL
            validate_url = URLValidator()
            try:
                validate_url(url)
            except ValidationError as e:
                return JsonResponse({'Status': False, 'Error': str(e)})
            else:
                response = get(url)
                stream = response.content
                print(f"Загружено {len(stream)} байт")
                print(f"Первые 200 символов: {stream[:200]}")
                print(f"Последние 200 символов: {stream[-200:]}")
                data = yaml.load(stream, Loader=YamlLoader)

        else:
            return JsonResponse({'Status': False, 'Errors': 'Необходимо указать URL или загрузить файл'})

        try:
            try:
                shop = Shop.objects.get(user_id=request.user.id)
            except Shop.DoesNotExist:
                shop_name = data.get('shop', f'Магазин {request.user.email}')
                shop = Shop.objects.create(name=shop_name, user_id=request.user.id)
            
            if 'categories' in data:
                for category in data['categories']:
                    category_object, _ = Category.objects.get_or_create(
                        id=category.get('id'), 
                        name=category.get('name')
                    )
                    category_object.shops.add(shop.id)
                    category_object.save()
            
            ProductInfo.objects.filter(shop_id=shop.id).delete()
            
            created_count = 0
            errors = []
            if 'goods' in data and data['goods']:
                for item in data['goods']:
                    try:
                        product, _ = Product.objects.get_or_create(
                            name=item.get('name', 'Неизвестный товар'), 
                            category_id=item.get('category')
                        )
                        product_info = ProductInfo.objects.create(
                            product_id=product.id,
                            external_id=item.get('id'),
                            model=item.get('model', ''),
                            price=item.get('price', 0),
                            price_rrc=item.get('price_rrc', 0),
                            quantity=item.get('quantity', 0),
                            shop_id=shop.id
                        )
                        
                        if 'parameters' in item:
                            for name, value in item['parameters'].items():
                                parameter_object, _ = Parameter.objects.get_or_create(name=name)
                                ProductParameter.objects.create(
                                    product_info_id=product_info.id,
                                    parameter_id=parameter_object.id,
                                    value=value
                                )
                        created_count += 1
                    except Exception as e:
                        error_msg = f"Ошибка при создании товара {item.get('name')}: {str(e)}"
                        errors.append(error_msg)
                        continue
        except Exception as e:
            return JsonResponse({'Status': False, 'Error': f'Ошибка обработки данных: {str(e)}'})

        response_data = {
            'Status': True, 
            'Message': f'Прайс-лист успешно изменен. Обновлено {created_count} товаров'
        }
        if errors:
            response_data['Errors'] = errors[:5]  # Показываем первые 5 ошибок
        return JsonResponse(response_data)


class PartnerState(APIView):
    """
    Управление состоянием партнера.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """
        Получить информацию о состоянии партнера.
        """
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)

        if request.user.type != 'shop':
            return JsonResponse({'Status': False, 'Error': 'Только для магазинов'}, status=403)

        try:
            shop = Shop.objects.get(user_id=request.user.id)
        except Shop.DoesNotExist:
            return JsonResponse({'Status': False, 'Error': 'Магазин не найден'}, status=404)
        
        serializer = ShopSerializer(shop)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        """
        Обновить информацию о состоянии партнера
        """
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)

        if request.user.type != 'shop':
            return JsonResponse({'Status': False, 'Error': 'Только для магазинов'}, status=403)
        
        state = request.data.get('state')
        if state:
            try:
                Shop.objects.filter(user_id=request.user.id).update(is_accepting_orders=strtobool(state))
                return JsonResponse({'Status': True, 'Message': 'Статус магазина успешно изменен'})
            except ValueError as error:
                return JsonResponse({'Status': False, 'Errors': str(error)})

        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})


class PartnerOrders(APIView):
    """
    Класс для получения заказов поставщиками
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """
        Retrieve the orders associated with the authenticated partner.
        """
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)

        if request.user.type != 'shop':
            return JsonResponse({'Status': False, 'Error': 'Только для магазинов'}, status=403)

        order = Order.objects.filter(
            ordered_items__product_info__shop__user_id=request.user.id).exclude(state='basket').prefetch_related(
            'ordered_items__product_info__product__category',
            'ordered_items__product_info__product_parameters__parameter').select_related('contact').annotate(
            total_sum=Sum(F('ordered_items__quantity') * F('ordered_items__product_info__price'))).distinct()

        serializer = OrderSerializer(order, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        """
        Изменить статус заказа магазином
        """
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)

        if request.user.type != 'shop':
            return JsonResponse({'Status': False, 'Error': 'Только для магазинов'}, status=403)

        if {'order_id', 'status'}.issubset(request.data):
            order_id = request.data['order_id']
            new_status = request.data['status']
            
            # Проверяем допустимые статусы
            allowed_statuses = ['confirmed', 'assembled', 'sent', 'delivered']
            if new_status not in allowed_statuses:
                return JsonResponse({
                    'Status': False, 
                    'Error': f'Недопустимый статус. Разрешены: {", ".join(allowed_statuses)}'
                })
            
            try:
                # Проверяем, что заказ принадлежит магазину
                order = Order.objects.filter(
                    id=order_id,
                    ordered_items__product_info__shop__user_id=request.user.id
                ).first()
                
                if not order:
                    return JsonResponse({'Status': False, 'Error': 'Заказ не найден'})
                
                old_status = order.state
                order.state = new_status
                order.save()
                
                # Создаем запись в истории статусов
                from backend.models import OrderStatusHistory
                OrderStatusHistory.objects.create(
                    order=order,
                    old_status=old_status,
                    new_status=new_status,
                    changed_by=request.user,
                    comment=f'Статус изменен магазином {request.user.email}'
                )
                
                status_names = {
                    'confirmed': 'Подтвержден',
                    'assembled': 'Собран', 
                    'sent': 'Отправлен',
                    'delivered': 'Доставлен'
                }
                
                return JsonResponse({
                    'Status': True,
                    'Message': f'Статус заказа #{order_id} изменен на "{status_names.get(new_status, new_status)}"'
                })
                
            except Exception as e:
                return JsonResponse({'Status': False, 'Error': f'Ошибка: {str(e)}'})
        
        return JsonResponse({'Status': False, 'Error': 'Не указаны все необходимые аргументы (order_id, status)'})