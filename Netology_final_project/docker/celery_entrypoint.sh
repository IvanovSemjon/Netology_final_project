set -e

if [ "$DJANGO_ENV" = "prod" ]; then
  export DJANGO_SETTINGS_MODULE="netology_pd_diplom.settings.prod"
else
  export DJANGO_SETTINGS_MODULE="netology_pd_diplom.settings.dev"
fi

echo "Starting Celery worker..."
celery -A backend.tasks.celery_app worker --loglevel=INFO