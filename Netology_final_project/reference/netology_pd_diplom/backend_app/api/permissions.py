from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Разрешение только владельцу объекта редактировать его.
    """
    def has_object_permission(self, request, view, obj):
        # Разрешения на чтение для любого запроса
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Разрешения на запись только владельцу объекта
        return obj.user == request.user


class IsShopOwner(permissions.BasePermission):
    """
    Разрешение только владельцу магазина.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.type == 'shop'


class IsBuyer(permissions.BasePermission):
    """
    Разрешение только покупателям.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.type == 'buyer'