# Интернет-магазин - Дипломный проект Netology

## Описание проекта

Backend API интернет-магазина, реализованный на **Django REST Framework**.  
Проект поддерживает каталог товаров, корзину, оформление заказов, партнёрские функции магазинов и административные операции.

Проект полностью **контейнеризирован с помощью Docker и Docker Compose**, использует **Celery + Redis** для асинхронных задач и предоставляет **автоматически генерируемую OpenAPI-документацию** (Swagger / Redoc) через **DRF-Spectacular**.

---
## Технологии

- **Backend:** Django 4.2.7, Django REST Framework 3.14.0  
- **База данных:** SQLite (dev) / PostgreSQL (через Docker)  
- **Асинхронные задачи:** Celery 5.3.4  
- **Broker / Backend:** Redis  
- **Контейнеризация:** Docker, Docker Compose  
- **Документация API:** DRF-Spectacular (OpenAPI 3.0)  
- **Аутентификация:** TokenAuthentication
- **Социальные провайдеры:** GitHub, Google, Yandex, VK
- **Email:** Django Email Backend  
- **Тестирование:** Django Test Framework


## Установка и запуск

### 1. Клонирование репозитория
```bash
git clone https://github.com/IvanovSemjon/Netology_final_project.git
cd Netology_final_project/reference/netology_pd_diplom
```

### 2. Запуск контейнеров
```bash
docker compose up --build
```
Будут запущены сервисы:
web — Django API
worker — Celery worker
redis — брокер сообщений

### 3. Применение миграций
```bash
docker compose exec web python manage.py migrate
```

### 4. Создание суперпользователя
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


Этот URL используется как BASE_URL и redirect_uri для Yandex OAuth.

### 🔁 Настройка Yandex OAuth

В .env:
BASE_URL=https://mynetology.loca.lt
SOCIAL_AUTH_YANDEX_CLIENT_ID=ваш_client_id
SOCIAL_AUTH_YANDEX_SECRET=ваш_client_secret


В панели разработчика Yandex:
Redirect URI:

https://mynetology.loca.lt/accounts/yandex/login/callback/


Разрешения: login:email и доступ к имени, фамилии и email пользователя.
Любое расхождение http/https или домена вызовет ошибку:
400 redirect_uri does not match the Callback URL

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
Метод	URL	                                    Описание
GET	    /api/v1/ ------------------------------ Информационная страница с эндпоинтами

### 🔐 Пользователи (регистрация, авторизация, профиль)
МетоД   URL	                                    Описание
POST	/api/v1/user/register/ ---------------- Регистрация пользователя
POST	/api/v1/user/register/confirm/ -------- Подтверждение email после регистрации
POST	/api/v1/user/login/ ------------------- Авторизацияпользователя
POST	/api/v1/user/password_reset/ ---------- Запрос на сброс пароля
POST	/api/v1/user/password_reset/confirm/ -- Подтверждение сброса пароля
GET	    /api/v1/user/details/ ----------------- Получение данных пользователя
PUT	    /api/v1/user/details/ ----------------- Полное обновление данных пользователя
PATCH	/api/v1/user/details/ ----------------- Частичное обновление данных пользователя
GET	    /api/v1/user/contact/ ----------------- Получение контактов пользователя
POST	/api/v1/user/contact/ ----------------- Создание контакта
PUT	    /api/v1/user/contact/ ----------------- Обновление контакта
DELETE	/api/v1/user/contact/ ----------------- Удаление контактов

### 🌐 Социальные логины (OAuth2)
Все через общий префикс /api/v1/auth/social/.

Метод	URL	                                    Описание
POST	/api/v1/auth/social/github/ ----------- Авторизация через GitHub
POST	/api/v1/auth/social/google/ ----------- Авторизация через Google
POST	/api/v1/auth/social/yandex/ ----------- Авторизация через Yandex

### ⚠️ Для Yandex обязательно использовать HTTPS для редиректа.

### 🛒 Корзина
Метод	URL	                  Описание
GET	    /api/v1/basket/ ----- Просмотр корзины
POST	/api/v1/basket/	----- Добавление товаров в корзину
PUT	    /api/v1/basket/	----- Обновление количества товаров
DELETE	/api/v1/basket/	----- Удаление товаров из корзины

### 🏷 Каталог товаров
Метод	URL	                     Описание
GET	    /api/v1/categories/ ---- Список категорий
GET	    /api/v1/products/ ------ Список продуктов
GET	    /api/v1/shops/ --------- Список магазинов

### 📝 Заказы
Метод	URL	                     Описание
GET	    /api/v1/order/ --------- Получение заказов пользователя
POST	/api/v1/order/ --------- Оформление заказа

### 🤝 Партнёры (магазины)
Метод	URL	                            Описание
GET	    /api/v1/partner/orders/	------- Получение заказов магазина
POST	/api/v1/partner/orders/	------- Обновление статуса заказа
GET	    /api/v1/partner/state/ -------- Получение состояния партнёра
POST	/api/v1/partner/state/ -------- Обновление состояния партнёра
POST	/api/v1/partner/update/	------- Обновление прайса партнёра

### 🛠 Админка
Метод	URL	                        Описание
POST	/api/v1/admin/import/ ----- Запуск импорта товаров

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

###  Структура проекта

```
backend/
├── api/
│   ├── serializers/           # Сериализаторы по модулям
│   │   ├── user.py           # Сериализаторы пользователей
│   │   ├── social.py         # Сериализаторы социальной аутентификации
│   │   └── ...
│   ├── views/
│   │   ├── auth.py           # Аутентификация
│   │   ├── social.py         # Социальная аутентификация
│   │   └── ...
│   ├── permissions.py        # Кастомные разрешения
│   └── urls.py              # API маршруты
├── models/                   # Модели данных
│   ├── users.py             # Модель пользователя
│   └── ...
├── adapters.py              # Адаптеры для allauth
├── services/                # Бизнес-логика
├── tasks/                   # Celery задачи
├── tests/                   # Тесты
├── management/              # Django команды
└── admin.py                # Настройки админки
```

## Особенности реализации

- **Мультиформатная аутентификация** - JWT токены + OAuth2 социальные провайдеры
- **Кастомная модель User** - с полями company, position, type
- **Токенная аутентификация** - безопасная авторизация через JWT
- **Разделение ролей** - покупатели и магазины с разными правами
- **Корзина как заказ** - корзина это заказ в статусе "basket"
- **Мультимагазинность** - один товар может продаваться в разных магазинах
- **История статусов** - отслеживание изменений статуса заказа
- **Валидация данных** - проверка корректности всех входных данных
- **Информативные ответы** - понятные сообщения об успехе и ошибках

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