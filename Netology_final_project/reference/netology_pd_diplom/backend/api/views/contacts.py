"""
Views для контактов.
"""

from backend.api.serializers import ContactSerializer
from backend.models import Contact
from django.db.models import Q
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


class ContactView(APIView):
    """
    Управление контактами.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """
        Получениеинформации о контактах.
        """
        contact = Contact.objects.filter(user_id=request.user.id)
        serializer = ContactSerializer(contact, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        """
        Добавить новый контакт.
        """
        if {"city", "street", "phone"}.issubset(request.data):
            contact_data = request.data.copy()
            contact_data["user"] = request.user.id
            serializer = ContactSerializer(data=contact_data)

            if serializer.is_valid():
                contact = serializer.save()
                return Response(
                    {
                        "status": True,
                        "message": "Контакт для доставки успешно создан",
                        "contact_id": contact.id,
                    },
                    status=status.HTTP_200_OK,
                )
            else:
                print(f"Ошибки валидации контакта: {serializer.errors}")
                return Response(
                    {"status": False, "errors": serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        return Response(
            {"status": False, "errors": "Не указаны все необходимые аргументы"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def delete(self, request, *args, **kwargs):
        """
        Удаление контакта.
        """
        items = request.data.get("items")

        if not isinstance(items, list) or not items:
            return Response(
                {"status": False, "errors": "items должен быть непустым массивом"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        query = Q()
        for contact_id in items:
            if isinstance(contact_id, int):
                query |= Q(id=contact_id, user_id=request.user.id)

        deleted_count = Contact.objects.filter(query).delete()[0]

        return Response(
            {"status": True, "deleted_objects": deleted_count},
            status=status.HTTP_200_OK,
        )

    def put(self, request, *args, **kwargs):
        """
        Скорректировать контакт.
        """
        if "id" in request.data:
            if request.data["id"].isdigit():
                contact = Contact.objects.filter(
                    id=request.data["id"], user_id=request.user.id
                ).first()
                if contact:
                    serializer = ContactSerializer(
                        contact, data=request.data, partial=True
                    )
                    if serializer.is_valid():
                        serializer.save()
                        return Response({"status": True}, status=status.HTTP_200_OK)
                    else:
                        return Response(
                            {"status": False, "errors": serializer.errors},
                            status=status.HTTP_400_BAD_REQUEST,
                        )

        return Response(
            {"status": False, "errors": "Не указаны все необходимые аргументы"},
            status=status.HTTP_400_BAD_REQUEST,
        )
