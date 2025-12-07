"""Модели связанные с импортом и экспортом данных"""
from django.db import models
from django.utils.translation import gettext_lazy as _

from .shops import Shop
from .users import User


class ImportTask(models.Model):
    """
    Задача импорта данных магазина.

    Отслеживает процесс загрузки и обработки файлов
    с товарами от магазинов-партнеров.
    """
    STATUS_PENDING = "pending"
    STATUS_PROCESSING = "processing"
    STATUS_COMPLETED = "completed"
    STATUS_FAILED = "failed"

    STATUS_CHOICES = (
        (STATUS_PENDING, _("Pending")),
        (STATUS_PROCESSING, _("Processing")),
        (STATUS_COMPLETED, _("Completed")),
        (STATUS_FAILED, _("Failed")),
    )

    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to="imports/%Y/%m/%d/")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    errors = models.JSONField(default=list, blank=True)
    imported_items = models.PositiveIntegerField(default=0)

    class Meta:
        """Метаданные модели ImportTask"""
        verbose_name = _("Задача импорта")
        verbose_name_plural = _("Список задач импорта")
        ordering = ("created_at",)

    def __str__(self) -> str:
        """Строковое представление модели ImportTask"""
        try:
            date_str = (
                self.created_at.strftime("%d.%m.%Y %H:%M")
                if self.created_at
                else "неизвестно"
            )
        except AttributeError:
            date_str = "неизвестно"
        return f"Импорт {self.shop.name} от {date_str}"


class ExportTask(models.Model):
    """
    Задача экспорта данных магазина.

    Управляет процессом создания и выгрузки файлов
    с данными о товарах для магазинов.
    """
    FORMAT_CSV = "csv"
    FORMAT_JSON = "json"
    FORMAT_XML = "xml"
    FORMAT_YAML = "yaml"
    FORMAT_XLSX = "xlsx"

    FORMAT_CHOICES = (
        (FORMAT_CSV, "CSV"),
        (FORMAT_JSON, "JSON"),
        (FORMAT_XML, "XML"),
        (FORMAT_YAML, "YAML"),
        (FORMAT_XLSX, "XLSX"),
    )

    shop = models.ForeignKey(Shop, related_name="export_tasks", on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name="export_tasks", on_delete=models.CASCADE)
    format = models.CharField(max_length=10, choices=FORMAT_CHOICES, default=FORMAT_YAML)
    file = models.FileField(upload_to="exports/%Y/%m/%d/", blank=True, null=True)
    status = models.CharField(
        max_length=20, choices=ImportTask.STATUS_CHOICES, default=ImportTask.STATUS_PENDING
        )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    errors = models.JSONField(default=list, blank=True)
    exported_items = models.PositiveIntegerField(default=0)
    export_params = models.JSONField(default=dict, blank=True)

    class Meta:
        """Метаданные модели ExportTask"""
        verbose_name = _("Задача экспорта")
        verbose_name_plural = _("Список задач экспорта")
        ordering = ("created_at",)
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["shop", "created_at"]),
            models.Index(fields=["user", "created_at"]),
        ]

    def __str__(self) -> str:
        """Строковое представление модели ExportTask"""
        try:
            date_str = (
                self.created_at.strftime("%d.%m.%Y %H:%M")
                if self.created_at
                else "неизвестно"
            )
        except AttributeError:
            date_str = "неизвестно"
        return f"Экспорт {self.shop.name} от {date_str}"
