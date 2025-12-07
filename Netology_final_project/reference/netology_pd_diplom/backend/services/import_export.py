"""Сервисы связанные с импортом и экспортом"""
from backend.models.tasks import ImportTask, ExportTask


class ImportExportService:
    """Сервис для управления задачами импорта и экспорта данных."""
    @staticmethod
    def start_import(task: ImportTask) -> None:
        """Запускает задачу импорта данных"""
        task.status = "processing"
        task.save(update_fields=["status"])

    @staticmethod
    def start_export(task: ExportTask) -> None:
        """Запускает задачу экспорта данных"""
        task.status = "processing"
        task.save(update_fields=["status"])

