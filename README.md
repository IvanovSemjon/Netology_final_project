# Интернет-магазин - Дипломный проект Netology

## Описание проекта

Backend API интернет-магазина, реализованный на **Django REST Framework**.  
Проект поддерживает каталог товаров, корзину, оформление заказов, партнёрские функции магазинов и административные операции.

Проект полностью **контейнеризирован с помощью Docker и Docker Compose**, использует **Celery + Redis** для асинхронных задач и предоставляет **автоматически генерируемую OpenAPI-документацию** (Swagger / Redoc) через **DRF-Spectacular**.

## Технологии

- **Backend:** Django 4.2.7, Django REST Framework 3.14.0  
- **База данных:** SQLite (dev) / PostgreSQL (через Docker)  
- **Асинхронные задачи:** Celery 5.3.4  
- **Broker / Backend:** Redis  
- **Контейнеризация:** Docker, Docker Compose  
- **Документация API:** DRF-Spectacular (OpenAPI 3.0)  
- **Аутентификация:** TokenAuthentication
- **Социальные провайдеры:** GitHub, Google, Yandex
- **Email:** Django Email Backend  
- **Тестирование:** Django Test Framework

## Предварительные требования

- **Python 3.10+** (для локального запуска без Docker)

- **Docker 24+ и Docker Compose 2+**

- **Node.js 18+ и npm** (для HTTPS-туннеля Yandex OAuth)

- **Redis** (через Docker или локально)

- **PostgreSQL** (для продакшена, через Docker или хост)


## Установка и запуск

### 1. Клонирование репозитория
```bash
git clone https://github.com/IvanovSemjon/Netology_final_project.git
cd Netology_final_project/reference/netology_pd_diplom
```

### 2. Настройка .env
Создайте .env файл с переменными (пример):

DEBUG=True
SECRET_KEY=your_secret_key
BASE_URL=https://mynetology.loca.lt
SOCIAL_AUTH_YANDEX_CLIENT_ID=ваш_client_id
SOCIAL_AUTH_YANDEX_SECRET=ваш_client_secret

### 3. Запуск контейнеров
```bash
docker compose up --build
```
Будут запущены сервисы:
web — Django API
worker — Celery worker
redis — брокер сообщений

### 4. Применение миграций
```bash
docker compose exec web python manage.py migrate
```

### 5. Создание суперпользователя
```bash
docker compose exec web python manage.py createsuperuser
```

### 🔐 Социальная аутентификация (OAuth)

Проект поддерживает социальную аутентификацию через:
✅ GitHub
✅ Google
✅ Yandex
Аутентификация реализована с использованием django-allauth и dj-rest-auth.

### ⚠️ Важно: HTTPS для Yandex

Яндекс строго требует HTTPS для redirect_uri.
Локальный http://localhost не работает для OAuth Yandex.
Для локальной разработки рекомендуется использовать HTTPS-туннель через Node.js.

### 🧩 Локальная разработка с HTTPS

Убедитесь, что Node.js установлен:

node -v
npm -v

Установите localtunnel:
```bash
npm install -g localtunnel
```

Запустите HTTPS-туннель на порт 8000:
```bash
lt --port 8000 --subdomain mynetology
```
В результате будет доступен URL вида:
https://mynetology.loca.lt

https://mynetology.loca.lt/accounts/yandex/login/callback/


### 🌐 Доступные социальные входы

✅ GitHub: https://mynetology.loca.lt/accounts/github/login/

✅ Google: https://mynetology.loca.lt/accounts/google/login/

✅ Yandex: https://mynetology.loca.lt/accounts/yandex/login/

### 🌐 Доступные сервисы
Сервис	                    URL

API	                        http://127.0.0.1:8000/api/v1/
Swagger	                    http://127.0.0.1:8000/api/v1/docs/swagger/
Redoc	                    http://127.0.0.1:8000/api/v1/docs/redoc/
Админка	                    http://127.0.0.1:8000/admin/
Redis	                    redis://redis:6379
Социальная аутентификация	http://127.0.0.1:8000/api/v1/auth/social/


### 📌 API v1
### Пользователи
Метод	URL	                                    Описание
POST	/api/v1/user/register/ ---------------- Регистрация пользователя
POST	/api/v1/user/register/confirm/ -------- Подтверждение email
POST	/api/v1/user/login/ ------------------- Авторизация
POST	/api/v1/user/password_reset/ ---------- Запрос на сброс пароля
POST	/api/v1/user/password_reset/confirm/ -- Подтверждение сброса пароля
GET 	/api/v1/user/details/ ----- Получение данных пользователя
PUT	    /api/v1/user/details/ ----- Полное обновление данных
PATCH	/api/v1/user/details/ ----- Частичное обновление данных
GET	    /api/v1/user/contact/ ----- Получение контактов
POST	/api/v1/user/contact/ ----- Создание контакта
PUT	    /api/v1/user/contact/ ----- Обновление контакта
DELETE	/api/v1/user/contact/ ----- Удаление контактов


### Социальные логины
Префикс: /api/v1/auth/social/
Методы POST для GitHub, Google, Yandex

### Корзина
Метод	URL	                    Описание
GET	    /api/v1/basket/ ------- Просмотр корзины
POST	/api/v1/basket/ ------- Добавление товаров
PUT	    /api/v1/basket/ ------- Обновление количества
DELETE	/api/v1/basket/ ------- Удаление товаров

### Каталог товаров
Метод	URL	                     Описание
GET	    /api/v1/categories/ ---- Список категорий
GET	    /api/v1/products/ ------ Список продуктов
GET	    /api/v1/shops/ --------- Список магазинов

### Заказы
Метод	URL	                Описание
GET     /api/v1/order/ ---- Получение заказов пользователя
POST	/api/v1/order/ ---- Оформление заказа

### Партнёры (магазины)
Метод	   URL	                Описание
GET     /api/v1/partner/orders/ ------- Получение заказов магазина
POST	/api/v1/partner/orders/ ------- Обновление статуса заказа
GET	    /api/v1/partner/state/ -------- Получение состояния партнёра
POST	/api/v1/partner/state/ -------- Обновление состояния партнёра
POST	/api/v1/partner/update/ ------- Загрузка прайса магазина (YAML/JSON)

### 🛠 Админка

✅Просмотр и управление пользователями, магазинами, товарами и заказами
✅Поддержка аватаров пользователей и изображений товаров
✅Русскоязычный интерфейс
✅Запуск импорта товаров через /api/v1/admin/import/

### 🧪 Тестирование
✅ 22 из 23 тестов успешно проходят (один ложный тест-модуль игнорируется)

# Все тесты приложения
```bash
docker compose exec web python manage.py test backend.tests --verbosity=2
```

### Покрытие тестами
✅ Аутентификация (6 тестов) — регистрация, вход, подтверждение email
✅ Заказы и корзина (5 тестов) — добавление, управление, оформление заказов
✅ Ограничение запросов (3 теста) — rate limiting для разных типов пользователей
✅ Валидаторы (8 тестов) — проверка паролей, телефонов, цен и количеств


### 📦 Кеширование (CacheOps + Redis)

Проект использует Redis и django-cacheops для кеширования запросов к базе данных. Это позволяет ускорить получение данных, таких как товары, категории и пользователи, уменьшить нагрузку на базу и повысить отзывчивость API.
Настройка кеша
- Redis настроен как backend для кеширования (redis://redis:6379/1).

CacheOps кеширует модели:
- auth.user — кешируется метод get на 15 минут.
- backend.productinfo — кешируются все запросы на 5 минут.

Кеш можно включать/отключать через переменную окружения:
```
CACHEOPS_ENABLED=True
```

Проверка работы кеша
В Django shell можно проверить разницу между запросом к базе и кешированным результатом:
```shell
from cacheops import invalidate_model
from backend.models import ProductInfo
```
# Очистка кеша
invalidate_model(ProductInfo)

# Первый запрос — идет в базу
products = list(ProductInfo.objects.all())

# Второй запрос — берется из кеша
products_cached = list(ProductInfo.objects.all())


Второй запрос выполняется быстрее, так как данные берутся из Redis.

### 🛡 Мониторинг и Sentry

Проект интегрирован с Sentry для мониторинга ошибок и производительности. Это позволяет:
- Отслеживать ошибки в Django-приложении.
- Получать информацию о пользователях и сессиях при ошибках.
- Анализировать производительность запросов.

# Настройка Sentry

DSN Sentry хранится в .env:
SENTRY_DSN=ваш_sentry_dsn

Интеграция автоматически подключена через sentry_sdk и DjangoIntegration.
При разработке (DEBUG=True) включена полная трассировка (traces_sample_rate=1.0), в продакшене — 10%.
Проверка работы Sentry

Для теста можно создать эндпоинт, который вызывает ошибку:

# urls.py
```shell
from django.urls import path
def trigger_error(request):
    1 / 0
urlpatterns += [path("sentry-debug/", trigger_error)]
```
Переход на /sentry-debug/ отправит тестовую ошибку в Sentry.

📊 Анализ производительности (django-silk)

В проекте используется django-silk — инструмент для анализа производительности Django-приложения.
Он позволяет выявлять неоптимальные ORM-запросы, избыточные обращения к базе данных (N+1 queries) и узкие места в обработке HTTP-запросов.

### 🔧 Возможности django-silk

✅ Логирование всех HTTP-запросов (API, админка)
✅ Анализ количества и времени выполнения SQL-запросов
✅ Обнаружение проблем типа N+1
✅ Просмотр стека вызовов Python-кода
✅ Таймлайн выполнения запроса
✅ Веб-интерфейс для визуального анализа

###  Структура проекта

```
backend/
├── api/
│   ├── serializers/
│   ├── views/
│   ├── permissions.py
│   └── urls.py
├── models/
├── adapters.py
├── services/
├── tasks/
├── tests/
├── management/
└── admin.py
```

## Особенности реализации

- Мультиформатная аутентификация (Token + OAuth2)
- Кастомная модель User с company, position, type
- Разделение ролей: покупатели и магазины
- Корзина реализована как заказ со статусом "basket"
- Мультимагазинность: один товар может быть в нескольких магазинах
- История изменений статусов заказов
- Валидация цен, количества, email, телефонов
- Асинхронная генерация миниатюр изображений через Celery

## Функциональность

### Для покупателей:
✅ Регистрация и подтверждение email
✅ Социальная аутентификация через GitHub, Google, VK
✅ Просмотр каталога товаров с фильтрацией
✅ Добавление товаров в корзину
✅ Управление корзиной (добавление, изменение, удаление)
✅ Создание контактов для доставки
✅ Оформление заказов
✅ Просмотр истории заказов

### Для магазинов:
✅ Загрузка прайс-листов (URL или файл)
✅ Управление статусом приема заказов
✅ Просмотр поступивших заказов
✅ Изменение статусов заказов
✅ Автоматическое создание товаров и категорий

### Административные функции:
✅ Управление пользователями и магазинами
✅ Просмотр всех заказов и товаров
✅ Управление социальными приложениями
✅ Русскоязычный интерфейс админки
✅ История изменений статусов заказов

## Контакты

**Автор:** Иванов Семён  
**Телефон:** +7-999-968-2498  
**Email:** ivanovsemjon@yandex.ru  
**GitHub:** https://github.com/IvanovSemjon/Netology_final_project  
**Проект:** Дипломная работа Netology - Django REST API интернет-магазина