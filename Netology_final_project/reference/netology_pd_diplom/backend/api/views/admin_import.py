"""
View для запуска Celery-задачи импорта товаров администратором.
"""

from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework import status

from backend.tasks.celery_tasks import do_import


class AdminImportView(APIView):
    """
    Запуск асинхронного импорта товаров.
    Доступно только администраторам.
    """

    permission_classes = [IsAdminUser]

    def post(self, request):
        """
        Запускает Celery-задачу импорта по переданному URL.
        """
        url = request.data.get("url")

        if not url:
            return Response(
                {"error": "URL не указан"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        task = do_import.delay(url)

        return Response(
            {
                "message": "Импорт запущен",
                "task_id": task.id,
                "status": "started",
            },
            status=status.HTTP_202_ACCEPTED,
        )
