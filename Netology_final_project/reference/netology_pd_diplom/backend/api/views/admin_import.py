"""
View для запуска Celery-задачи импорта товаров администратором.
"""

from backend.tasks.celery_tasks import do_import
from drf_spectacular.utils import extend_schema
from rest_framework import serializers, status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView


class AdminImportRequestSerializer(serializers.Serializer):
    """
    Сериализатор для запроса запуска импорта.
    """
    url = serializers.URLField(
        help_text="URL для импорта товаров",
        required=True
    )


class AdminImportResponseSerializer(serializers.Serializer):
    """
    Сериализатор для успешного ответа.
    """
    message = serializers.CharField()
    task_id = serializers.CharField()
    status = serializers.CharField()


class AdminImportErrorSerializer(serializers.Serializer):
    """
    Сериализатор для ошибки запроса.
    """
    error = serializers.CharField()


class AdminImportView(APIView):
    """
    Запуск асинхронного импорта товаров.
    Доступно только администраторам.
    """

    permission_classes = [IsAdminUser]

    @extend_schema(
        summary="Запуск импорта товаров",
        description="Запускает Celery-задачу импорта товаров по переданному URL. Доступно только администраторам.",
        request=AdminImportRequestSerializer,
        responses={
            202: AdminImportResponseSerializer,
            400: AdminImportErrorSerializer
        },
        tags=['Админ']
    )
    def post(self, request):
        """
        Запускает Celery-задачу импорта по переданному URL.
        """
        serializer = AdminImportRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"error": "URL не указан или некорректен"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        url = serializer.validated_data["url"]
        task = do_import.delay(url)

        return Response(
            {
                "message": "Импорт запущен",
                "task_id": task.id,
                "status": "started",
            },
            status=status.HTTP_202_ACCEPTED,
        )