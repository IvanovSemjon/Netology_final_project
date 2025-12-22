"""
Разрешения для API.
"""

from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Разрешение: только владелец объекта может редактировать его.
    SAFE_METHODS (GET, HEAD, OPTIONS) разрешены всем.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return getattr(obj, "user", None) == request.user


class IsShopOwner(permissions.BasePermission):
    """
    Разрешение: только пользователи типа 'shop'.
    """

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and getattr(request.user, "type", None) == "shop"
        )


class IsBuyer(permissions.BasePermission):
    """
    Разрешение: только пользователи типа 'buyer'.
    """

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and getattr(request.user, "type", None) == "buyer"
        )
