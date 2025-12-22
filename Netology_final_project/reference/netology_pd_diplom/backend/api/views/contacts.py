from backend.api.serializers import ContactSerializer
from backend.models import Contact
from django.db.models import Q
from rest_framework import status, serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiResponse

class ContactCreateSerializer(serializers.Serializer):
    city = serializers.CharField(required=True)
    street = serializers.CharField(required=True)
    phone = serializers.CharField(required=True)
    house = serializers.CharField(required=False, allow_blank=True)
    structure = serializers.CharField(required=False, allow_blank=True)
    building = serializers.CharField(required=False, allow_blank=True)
    apartment = serializers.CharField(required=False, allow_blank=True)

class ContactDeleteSerializer(serializers.Serializer):
    items = serializers.ListField(child=serializers.IntegerField(), required=True)

class ContactUpdateSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    city = serializers.CharField(required=False)
    street = serializers.CharField(required=False)
    phone = serializers.CharField(required=False)
    house = serializers.CharField(required=False, allow_blank=True)
    structure = serializers.CharField(required=False, allow_blank=True)
    building = serializers.CharField(required=False, allow_blank=True)
    apartment = serializers.CharField(required=False, allow_blank=True)

class ContactView(APIView):
    """
    Управление контактами пользователя.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Получение контактов",
        description="Возвращает список всех контактов текущего пользователя.",
        responses=ContactSerializer(many=True),
        tags=['Контакты']
    )
    def get(self, request, *args, **kwargs):
        contact = Contact.objects.filter(user_id=request.user.id)
        serializer = ContactSerializer(contact, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Создание контакта",
        description="Создает новый контакт для пользователя.",
        request=ContactCreateSerializer,
        responses={
            200: OpenApiResponse(description="Контакт создан", response=ContactSerializer)
        },
        tags=['Контакты']
    )
    def post(self, request, *args, **kwargs):
        if {"city", "street", "phone"}.issubset(request.data):
            contact_data = request.data.copy()
            contact_data["user"] = request.user.id
            serializer = ContactSerializer(data=contact_data)
            if serializer.is_valid():
                contact = serializer.save()
                return Response({
                    "status": True,
                    "message": "Контакт для доставки успешно создан",
                    "contact_id": contact.id,
                }, status=status.HTTP_200_OK)
            return Response({"status": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"status": False, "errors": "Не указаны все необходимые аргументы"}, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Удаление контактов",
        description="Удаляет указанные контакты пользователя.",
        request=ContactDeleteSerializer,
        responses={200: OpenApiResponse(description="Количество удаленных объектов")},
        tags=['Контакты']
    )
    def delete(self, request, *args, **kwargs):
        items = request.data.get("items")
        if not isinstance(items, list) or not items:
            return Response({"status": False, "errors": "items должен быть непустым массивом"}, status=status.HTTP_400_BAD_REQUEST)
        query = Q()
        for contact_id in items:
            if isinstance(contact_id, int):
                query |= Q(id=contact_id, user_id=request.user.id)
        deleted_count = Contact.objects.filter(query).delete()[0]
        return Response({"status": True, "deleted_objects": deleted_count}, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Обновление контакта",
        description="Обновляет указанный контакт пользователя.",
        request=ContactUpdateSerializer,
        responses={200: OpenApiResponse(description="Контакт обновлен")},
        tags=['Контакты']
    )
    def put(self, request, *args, **kwargs):
        if "id" in request.data:
            contact_id = request.data["id"]
            if str(contact_id).isdigit():
                contact = Contact.objects.filter(id=contact_id, user_id=request.user.id).first()
                if contact:
                    serializer = ContactSerializer(contact, data=request.data, partial=True)
                    if serializer.is_valid():
                        serializer.save()
                        return Response({"status": True}, status=status.HTTP_200_OK)
                    return Response({"status": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"status": False, "errors": "Не указаны все необходимые аргументы"}, status=status.HTTP_400_BAD_REQUEST)