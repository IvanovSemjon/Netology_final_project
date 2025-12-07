FROM python:3.10-slim

# Установка системных зависимостей
RUN apt-get update && apt-get install -y gcc libpq-dev

# Создаём рабочую директорию
WORKDIR /app

# Копируем зависимости
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Копируем весь проект
COPY ./reference/netology_pd_diplom /app

# Указываем порт
EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
