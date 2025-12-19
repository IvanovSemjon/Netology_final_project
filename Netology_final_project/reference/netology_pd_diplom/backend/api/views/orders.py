from django.db import IntegrityError
from django.db.models import Sum, F
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework.views import APIView

from backend.models import Order
from backend.api.serializers import OrderSerializer
from backend.signals import new_order
from backend.services.emails import send_order_confirmation_email
from rest_framework.permissions import IsAuthenticated, AllowAny


class OrderView(APIView):
    """
    Класс для получения и размещения заказов пользователями
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """
        Получить информацию о заказах
        """
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)
        
        order = Order.objects.filter(
            user_id=request.user.id).exclude(state='basket').prefetch_related(
            'ordered_items__product_info__product__category',
            'ordered_items__product_info__product_parameters__parameter').select_related('contact').annotate(
            total_sum=Sum(F('ordered_items__quantity') * F('ordered_items__product_info__price'))).distinct()

        serializer = OrderSerializer(order, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        """
        Оформить заказ и отправить уведомление
        """
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)

        if {'id', 'contact'}.issubset(request.data):
            if request.data['id'].isdigit():
                try:
                    is_updated = Order.objects.filter(
                        user_id=request.user.id, id=request.data['id']).update(
                        contact_id=request.data['contact'],
                        state='new')
                except IntegrityError as error:
                    print(error)
                    return JsonResponse({'Status': False, 'Errors': 'Неправильно указаны аргументы'})
                else:
                    if is_updated:
                        order = Order.objects.get(id=request.data['id'])
                        new_order.send(sender=self.__class__, user_id=request.user.id)
                        send_order_confirmation_email(order)
                        return JsonResponse({'Status': True, 'Message': 'Заказ подтвержден. Уведомление отправлено на email.'})

        return JsonResponse({'Status': False, 'Error': 'Не указаны все необходимые аргументы'})