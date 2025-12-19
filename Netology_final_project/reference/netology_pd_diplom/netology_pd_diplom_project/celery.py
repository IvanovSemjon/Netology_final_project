import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "netology_pd_diplom_project.settings")

app = Celery("netology_pd_diplom_project")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
