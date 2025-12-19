"""Фоновые задачи"""
from celery import shared_task

from backend.models.tasks import ImportTask  # pylint: disable=import-error
from backend.services.import_export import ImportExportService  # pylint: disable=import-error

@shared_task(bind=True, max_retries=3)
def handle_import(self, task_id: int):  # pylint: disable=unused-argument
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
