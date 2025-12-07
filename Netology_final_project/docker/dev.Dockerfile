FROM python:3.12

WORKDIR /app

COPY ./reference/netology_pd_diplom /app

RUN pip install --no-cache-dir -r requirements.txt

ENV DJANGO_ENV=dev

COPY ./docker/entrypoint.sh /entrypoint.sh
COPY ./docker/celery_entrypoint.sh /celery_entrypoint.sh
RUN chmod +x /entrypoint.sh /celery_entrypoint.sh

CMD ["/entrypoint.sh"]