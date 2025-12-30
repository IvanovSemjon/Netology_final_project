import os
from pathlib import Path
from datetime import timedelta

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

# ======================================================
# Основа
# ======================================================

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "dev-key")
DEBUG = os.getenv("DJANGO_DEBUG", "True") == "True"

ALLOWED_HOSTS = ["*"]

# ======================================================
# Логирование
# ======================================================

SENTRY_DSN = os.getenv(
    "SENTRY_DSN",
    "https://085b1f04b3f861cfe4aa6545f96284e1@o4510618682064896.ingest.de.sentry.io/4510618693075024"
)

sentry_sdk.init(
    dsn=SENTRY_DSN,
    integrations=[DjangoIntegration()],
    send_default_pii=True,
    traces_sample_rate=1.0 if DEBUG else 0.1,
)

# ======================================================
# Приложения
# ======================================================

DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "django_rest_passwordreset",
]

THIRD_PARTY_APPS = [
    "rest_framework",
    "rest_framework.authtoken",
    "drf_spectacular",
    "dj_rest_auth",
    "dj_rest_auth.registration",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.github",
    "allauth.socialaccount.providers.google",
    "allauth.socialaccount.providers.yandex",
    "versatileimagefield",
    "cacheops",
    "corsheaders",
    "silk",
]

LOCAL_APPS = [
    "backend.apps.BackendConfig",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# ======================================================
# Аутентификация
# ======================================================

AUTH_USER_MODEL = "backend.User"
SITE_ID = 1

AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
)

ACCOUNT_ADAPTER = "backend.api.adapters.CustomAccountAdapter"
SOCIALACCOUNT_ADAPTER = "backend.api.adapters.CustomSocialAccountAdapter"

ACCOUNT_SIGNUP_FIELDS = ["email"]

LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"

SOCIALACCOUNT_LOGIN_ON_GET = True

# ======================================================
# Токены
# ======================================================

REST_USE_JWT = True

REST_AUTH_REGISTER_SERIALIZER = (
    "backend.api.serializers.user.CustomRegisterSerializer"
)

JWT_AUTH_COOKIE = "jwt-auth"
JWT_AUTH_REFRESH_COOKIE = "jwt-refresh-token"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework.authentication.TokenAuthentication",
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "EXCEPTION_HANDLER": "backend.api.exceptions.custom_exception_handler",
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.UserRateThrottle",
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.ScopedRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "user": "111/day",
        "anon": "17/day",
        "basket": "5/min",
        "account": "6/min",
        "dj_rest_auth": "10/min",
    },
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIMS": "user_id",
}

# ======================================================
# Социальная авторизация
# ======================================================

USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

SOCIALACCOUNT_PROVIDERS = {
    "github": {
        "APP": {
            "client_id": os.getenv("SOCIAL_AUTH_GITHUB_CLIENT_ID"),
            "secret": os.getenv("SOCIAL_AUTH_GITHUB_SECRET"),
            "key": "",
        },
        "SCOPE": ["user:email"],
    },
    "google": {
        "APP": {
            "client_id": os.getenv("SOCIAL_AUTH_GOOGLE_CLIENT_ID"),
            "secret": os.getenv("SOCIAL_AUTH_GOOGLE_SECRET"),
            "key": "",
        },
        "SCOPE": ["profile", "email"],
    },
    "yandex": {
        "APP": {
            "client_id": os.getenv("SOCIAL_AUTH_YANDEX_CLIENT_ID"),
            "secret": os.getenv("SOCIAL_AUTH_YANDEX_SECRET"),
            "key": "",
        },
        "SCOPE": ["login:email"],
    },
}

# ======================================================
# Мидлварь
# ======================================================

MIDDLEWARE = [
    "silk.middleware.SilkyMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    # 'cacheops.middleware.CacheOpsMiddleware',
    "allauth.account.middleware.AccountMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

CORS_ALLOW_ALL_ORIGINS = True

CORS_ALLOWED_ORIGINS = [
    "https://mynetology.loca.lt",
    "http://localhost:8000",
]
# ======================================================
# Урлы
# ======================================================

ROOT_URLCONF = "netology_pd_diplom_project.urls"
WSGI_APPLICATION = "netology_pd_diplom_project.wsgi.application"

# ======================================================
# Шаблоны
# ======================================================

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# ======================================================
# БД
# ======================================================

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# ======================================================
# Статика
# ======================================================

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# ======================================================
# Селери
# ======================================================

CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/0")
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = "Europe/Moscow"

if os.name == "nt":
    CELERYD_POOL = "solo"

# ======================================================
# Почта
# ======================================================

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
DEFAULT_FROM_EMAIL = "webmaster@localhost"

# ======================================================
# Документация
# ======================================================

SPECTACULAR_SETTINGS = {
    "TITLE": "Netology Diploma API",
    "DESCRIPTION": "Backend API для дипломного проекта",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "SCHEMA_PATH_PREFIX": r"/api",
    "COMPONENT_SPLIT_REQUEST": True,
    "SECURITY": [{"BearerAuth": []}],
    "SECURITY_SCHEMES": {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    },
}

# ======================================================
# Аватарки
# ======================================================

VERSATILEIMAGEFIELD_SETTINGS = {
    "cache_length": 2592000,
    "cache_name": "versatileimagefield_cache",
}

VERSATILEIMAGEFIELD_RENDITION_KEY_SETS = {
    "user_avatar": [
        ("small", "crop__100x100"),
        ("medium", "crop__300x300"),
    ],
    "product_image": [
        ("small", "crop__150x150"),
        ("medium", "resize_to_limit__800x800"),
    ],
}

# ======================================================
# Кеширование
# ======================================================

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://redis:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

CACHEOPS_REDIS = {
    'host': 'redis',
    'port': 6379,
    'db': 1,
    'socket_timeout': 3,
}

CACHEOPS_DEFAULTS = {
    'timeout': 60 * 15,
}

CACHEOPS = {
    'auth.user': {'ops': 'get', 'timeout': 60*15},
    'backend.productinfo': {'ops': 'all', 'timeout': 60*5},
}

CACHEOPS_ENABLED = os.getenv("CACHEOPS_ENABLED", "True") == "True"

# ======================================================
# Силк
# ======================================================
SILKY_PYTHON_PROFILER = True
SILKY_AUTHENTICATION = True  # только авторизованные пользователи
SILKY_AUTHORISATION = True
SILKY_MAX_REQUEST_BODY_SIZE = -1  # чтобы профилировать любые размеры запросов