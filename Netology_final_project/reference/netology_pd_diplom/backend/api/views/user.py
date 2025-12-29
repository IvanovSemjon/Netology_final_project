from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from backend.api.serializers.user import UserDetailsSerializer


class AccountDetailsWithAvatar(APIView):
    """
    Получение и обновление данных пользователя + загрузка аватара
    """
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    @extend_schema(
        request=None,
        responses=UserDetailsSerializer,
        description="Получение данных пользователя"
    )
    def get(self, request):
        serializer = UserDetailsSerializer(request.user)
        return Response(serializer.data)

    @extend_schema(
        request=UserDetailsSerializer,
        responses=UserDetailsSerializer,
        description="Частичное обновление данных пользователя"
    )
    def patch(self, request):
        serializer = UserDetailsSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @extend_schema(
        request=UserDetailsSerializer,
        responses=UserDetailsSerializer,
        description="Полное обновление данных пользователя"
    )
    def put(self, request):
        serializer = UserDetailsSerializer(request.user, data=request.data, partial=False)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)