import os
from pathlib import Path
from datetime import timedelta

# ======== BASE ========
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "dev-key")
DEBUG = os.getenv("DJANGO_DEBUG", "True") == "True"
ALLOWED_HOSTS = ['*']

# ======== APPS ========
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django_rest_passwordreset',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'rest_framework.authtoken',
    'drf_spectacular',
    'dj_rest_auth',
    'dj_rest_auth.registration',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.github',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.yandex',
]

LOCAL_APPS = [
    'backend.apps.BackendConfig',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# ======== AUTH ========
AUTH_USER_MODEL = 'backend.User'
SITE_ID = 1

AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
)

ACCOUNT_ADAPTER = 'backend.api.adapters.CustomAccountAdapter'
SOCIALACCOUNT_ADAPTER = 'backend.api.adapters.CustomSocialAccountAdapter'

ACCOUNT_SIGNUP_FIELDS = ["email"]

# ======== DJ REST AUTH ========
REST_AUTH_REGISTER_SERIALIZER = "backend.api.serializers.user.CustomRegisterSerializer"
REST_USE_JWT = True
JWT_AUTH_COOKIE = 'jwt-auth'
JWT_AUTH_REFRESH_COOKIE = 'jwt-refresh-token'

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework.authentication.TokenAuthentication",
        "dj_rest_auth.jwt_auth.JWTCookieAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.AllowAny",
    ),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "EXCEPTION_HANDLER": "backend.api.exceptions.custom_exception_handler",
    "DEFAULT_THROTTLE_CLASSES": [
        'rest_framework.throttling.UserRateThrottle',
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.ScopedRateThrottle',
    ],
    "DEFAULT_THROTTLE_RATES": {
        "user": "111/day",
        "anon": "17/day",
        "basket": "5/min",
        "account": "6/min",
        "dj_rest_auth": "10/min",
    }
}

# ======== SOCIAL ========
SOCIALACCOUNT_PROVIDERS = {
    'github': {
        'APP': {
            'client_id': os.getenv('SOCIAL_AUTH_GITHUB_CLIENT_ID'),
            'secret': os.getenv('SOCIAL_AUTH_GITHUB_SECRET'),
            'key': ''
        },
        'SCOPE': ['user:email'],
        'METHOD': 'oauth2',
        'VERIFIED_EMAIL': True,
    },
    'google': {
        'APP': {
            'client_id': os.getenv('SOCIAL_AUTH_GOOGLE_CLIENT_ID'),
            'secret': os.getenv('SOCIAL_AUTH_GOOGLE_SECRET'),
            'key': ''
        },
        'SCOPE': ['profile', 'email'],
        'AUTH_PARAMS': {'access_type': 'online'},
        'OAUTH_PKCE_ENABLED': True,
    },
    'yandex': {
    'APP': {
        'client_id': os.getenv('SOCIAL_AUTH_YANDEX_CLIENT_ID'),
        'secret': os.getenv('SOCIAL_AUTH_YANDEX_SECRET'),
        'key': ''
    },
    'SCOPE': ['login:email'],
    'AUTH_PARAMS': {},
},
}

SOCIAL_CALLBACK_URLS = {
    'github': os.getenv('GITHUB_CALLBACK_URL', 'http://localhost:8000/accounts/github/login/callback/'),
    'google': os.getenv('GOOGLE_CALLBACK_URL', 'http://localhost:8000/accounts/google/login/callback/'),
    'yandex': os.getenv('YANDEX_CALLBACK_URL', 'http://localhost:8000/accounts/yandex/login/callback/'),
}

BASE_URL = os.getenv('BASE_URL', 'http://localhost:8000')

LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

SOCIALACCOUNT_LOGIN_ON_GET = True

# ======== MIDDLEWARE ========
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'netology_pd_diplom_project.urls'

# ======== TEMPLATES ========
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'netology_pd_diplom_project.wsgi.application'

# ======== DATABASE ========
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ======== STATIC ========
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# ======== CELERY ========
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/0")
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Europe/Moscow'
CELERYD_POOL_RESTARTS = True
if os.name == "nt":
    CELERYD_POOL = "solo"

# ======== EMAIL ========
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = "webmaster@localhost"

# ======== SPECTACULAR / SWAGGER ========
SPECTACULAR_SETTINGS = {
    'TITLE': 'Netology Diploma API',
    'DESCRIPTION': 'Backend API для дипломного проекта',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'SCHEMA_PATH_PREFIX': r'/api',
    'COMPONENT_SPLIT_REQUEST': True,
    'SECURITY': [{'BearerAuth': []}],
    'SECURITY_SCHEMES': {
        'TokenAuth': {'type': 'apiKey', 'in': 'header', 'name': 'Authorization'}
    },
}

# ======== SIMPLE JWT ========
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIMS': 'user_id',
}