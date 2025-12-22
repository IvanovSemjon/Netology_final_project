"""Сервисы связанные с заказами"""
# pylint: disable=no-member
from typing import Optional
from django.db import transaction

from backend.models.orders import Order, OrderState, OrderStatusHistory
from backend.services.inventory import InventoryService
from backend.signals import order_status_changed


class OrderServiceError(Exception):
    """
    Исключение для ошибок сервиса управления заказами.
    
    """    
    pass


class OrderService:
    """
    Сервис для управления заказами и их статусами.
    
    """
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

        """
        old_status = order.state

        if old_status == new_status:
            return

        if old_status == OrderState.BASKET and new_status == OrderState.NEW:
            InventoryService.reserve_for_order(order)

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

        order_status_changed.send(
            sender=OrderService,
            order_id=order.id,
            old_status=old_status,
            new_status=new_status,
        )
