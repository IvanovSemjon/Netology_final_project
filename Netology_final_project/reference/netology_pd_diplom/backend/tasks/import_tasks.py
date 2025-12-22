"""
Фоновые задачи.
"""

from backend.models.tasks import ImportTask
from backend.services.import_export import ImportExportService
from celery import shared_task


@shared_task(bind=True, max_retries=3)
def handle_import(self, task_id: int):
    """
    Обрабатывает задачу импорта данных в фоновом режиме.
    """
    task = ImportTask.objects.get(pk=task_id)
    try:
        ImportExportService.process_import(task)
        task.status = "completed"
        task.save(update_fields=["status"])
    except Exception as exc:
        task.status = "failed"
        task.errors = [str(exc)]
        task.save(update_fields=["status", "errors"])
        raise self.retry(exc=exc)
