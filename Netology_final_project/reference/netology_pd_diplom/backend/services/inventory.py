"""Сервисы отвечающие за бизнес логику"""
# pylint: disable=no-member
from django.db import transaction
from django.db.models import F

from backend.models.catalog import ProductInfo
from backend.models.orders import Order


class InventoryError(Exception):
    """
    Исключение для ошибок управления складскими запасами.
    
    """


class InventoryService:
    """
    Сервис для управления складскими запасами и резервированием товаров.
    
    """
    @staticmethod
    def reserve_for_order(order: Order) -> None:
        """
        Резервирует товары для заказа атомарно.

        """
        with transaction.atomic():
            # получаем список товаров в наличии
            required = {}
            for item in order.ordered_items.select_related("product_info"):
                pid = item.product_info_id
                required.setdefault(pid, 0)
                required[pid] += item.quantity

            # проверяем доступность
            qset = ProductInfo.objects.filter(id__in=required.keys()).select_for_update()
            avail_map = {p.id: p.quantity for p in qset}

            for pid, need in required.items():
                if avail_map.get(pid, 0) < need:
                    raise InventoryError(f"Not enough stock for product_info {pid}")

            # делаем update с F выражением
            for pid, need in required.items():
                ProductInfo.objects.filter(id=pid).update(quantity=F("quantity") - need)

    @staticmethod
    def release_for_order(order: Order) -> None:
        """
        Возвращает резерв назад на склад.
        
        """
        with transaction.atomic():
            required = {}
            for item in order.ordered_items.select_related("product_info"):
                pid = item.product_info_id
                required.setdefault(pid, 0)
                required[pid] += item.quantity

            for pid, qty in required.items():
                ProductInfo.objects.filter(id=pid).update(quantity=F("quantity") + qty)
