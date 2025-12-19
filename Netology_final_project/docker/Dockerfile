# Используем легковесный Python
FROM python:3.10-slim

# Установка системных зависимостей
RUN apt-get update && apt-get install -y gcc libpq-dev && rm -rf /var/lib/apt/lists/*

# Создаём рабочую директорию
WORKDIR /app

# Копируем зависимости и устанавливаем
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Копируем проект
COPY ./reference/netology_pd_diplom /app

# Указываем порт для Django
EXPOSE 8000

# Устанавливаем переменные окружения для Python
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Команда по умолчанию — запуск Django
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]