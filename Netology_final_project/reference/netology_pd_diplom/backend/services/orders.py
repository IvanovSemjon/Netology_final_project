"""Сервисы связанные с заказами"""
# pylint: disable=no-member
from typing import Optional

from django.db import transaction

from backend.models.orders import Order, OrderState, OrderStatusHistory
from backend.services.inventory import InventoryService, InventoryError
from backend.signals import order_status_changed


class OrderServiceError(Exception):
    """Исключение для ошибок сервиса управления заказами."""

class OrderService:
    """Сервис для управления заказами и их статусами."""
    @staticmethod
    @transaction.atomic
    def change_status(
        order: Order,
        new_status: str,
        changed_by: Optional[int] = None,
        comment: str = ""
        ) -> None:
        """
        Изменяет статус заказа с автоматическим управлением складскими запасами.
        
        Args:
            order: Заказ для изменения статуса
            new_status: Новый статус заказа
            changed_by: ID пользователя, изменившего статус (опционально)
            comment: Комментарий к изменению
            
        Raises:
            OrderServiceError: При ошибках резервирования товаров
        """
        old_status = order.state

        if old_status == new_status:
            return

        if old_status == OrderState.BASKET and new_status == OrderState.NEW:
            try:
                InventoryService.reserve_for_order(order)
            except InventoryError as exc:
                raise OrderServiceError(str(exc)) from exc

        if old_status != OrderState.CANCELED and new_status == OrderState.CANCELED:
            InventoryService.release_for_order(order)

        order.state = new_status
        order.save(update_fields=["state"])

        OrderStatusHistory.objects.create(
            order=order,
            old_status=old_status,
            new_status=new_status,
            changed_by_id=changed_by,
            comment=comment,
        )
        
        # Отправляем сигнал об изменении статуса
        order_status_changed.send(
            sender=self.__class__,
            user_id=order.user_id,
            order_id=order.id,
            old_status=old_status,
            new_status=new_status
        )

class OrderView(APIView):

    def get(self, request):
        orders = OrderService.list_user_orders(request.user)
        return Response(OrderSerializer(orders, many=True).data)

    def post(self, request):
        order = OrderService.create_order(request.user, request.data)
        return Response(OrderSerializer(order).data)