set -e

if [ "$DJANGO_ENV" = "prod" ]; then
  export DJANGO_SETTINGS_MODULE="netology_pd_diplom.settings.prod"
else
  export DJANGO_SETTINGS_MODULE="netology_pd_diplom.settings.dev"
fi

python manage.py migrate

if [ "$DJANGO_ENV" = "prod" ]; then
    python manage.py collectstatic --noinput
    exec gunicorn netology_pd_diplom.wsgi:application --bind 0.0.0.0:8000
else
    exec python manage.py runserver 0.0.0.0:8000
fi