# Импорты для обратной совместимости
from .user import UserSerializer
from .contact import ContactSerializer
from .category import CategorySerializer
from .shop import ShopSerializer
from .product import ProductSerializer, ProductParameterSerializer, ProductInfoSerializer
from .order import OrderItemSerializer, OrderItemCreateSerializer, OrderSerializer

__all__ = [
    'UserSerializer',
    'ContactSerializer', 
    'CategorySerializer',
    'ShopSerializer',
    'ProductSerializer',
    'ProductParameterSerializer', 
    'ProductInfoSerializer',
    'OrderItemSerializer',
    'OrderItemCreateSerializer',
    'OrderSerializer'
]