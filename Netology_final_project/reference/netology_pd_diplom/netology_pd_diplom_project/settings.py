import os
import sys
from pathlib import Path
from django.conf import settings

ACCOUNT_ADAPTER = 'backend.adapters.CustomAccountAdapter'
SOCIALACCOUNT_ADAPTER = 'backend.adapters.CustomSocialAccountAdapter'

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "dev-key")

DEBUG = os.getenv("DJANGO_DEBUG", "True") == "True"

ALLOWED_HOSTS = ['*']

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
    # rest часть
    "dj_rest_auth",
    "dj_rest_auth.registration",
    'rest_framework',
    'rest_framework.authtoken',
    'drf_spectacular',

    # auth часть
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.github',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.yandex',
    'allauth.socialaccount.providers.vk',
]

LOCAL_APPS = [
    'backend.apps.BackendConfig',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

AUTH_USER_MODEL = 'backend.User'

SITE_ID = 1

AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
)

ACCOUNT_EMAIL_VERIFICATION = 'optional'
SOCIALACCOUNT_EMAIL_VERIFICATION = 'none'
ACCOUNT_EMAIL_REQUIRED = True
SOCIALACCOUNT_EMAIL_REQUIRED = True
SOCIALACCOUNT_AUTO_SIGNUP = True
SOCIALACCOUNT_STORE_TOKENS = True

ACCOUNT_USER_MODEL_USERNAME_FIELD = 'email'
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_AUTHENTICATION_METHOD = 'email'

REST_AUTH_REGISTER_SERIALIZER = "backend.api.serializers.user.CustomRegisterSerializer"

REST_USE_JWT = True
JWT_AUTH_COOKIE = 'jwt-auth'
JWT_AUTH_REFRESH_COOKIE = 'jwt-refresh-token'


SOCIALACCOUNT_PROVIDERS = {
    'vk': {
        'APP': {
            'client_id': os.getenv('SOCIAL_AUTH_VK_CLIENT_ID'),
            'secret': os.getenv('SOCIAL_AUTH_VK_SECRET'),
            'key': ''
        },
        'SCOPE': ['email'],
        'AUTH_PARAMS': {'v': '5.131'},
    },
    'yandex': {
        'APP': {
            'client_id': os.getenv('SOCIAL_AUTH_YANDEX_CLIENT_ID'),
            'secret': os.getenv('SOCIAL_AUTH_YANDEX_SECRET'),
            'key': ''
        },
        'SCOPE': ['login:email'],
    },
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
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        },
        'OAUTH_PKCE_ENABLED': True,
    }
}

ACCOUNT_SIGNUP_FIELDS = {
    'email': {
        'required': True,
        'placeholder': 'Электронная почта',
    },
    'username': {
        'required': False,
        'placeholder': 'Имя пользователя (опционально)',
    },
    'first_name': {
        'required': True,
        'placeholder': 'Имя',
    },
    'last_name': {
        'required': True,
        'placeholder': 'Фамилия',
    },
}

ACCOUNT_CONFIRM_EMAIL_ON_GET = True
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 3
ACCOUNT_EMAIL_CONFIRMATION_COOLDOWN = 180
ACCOUNT_EMAIL_CONFIRMATION_AUTHENTICATED_REDIRECT_URL = '/'
ACCOUNT_EMAIL_CONFIRMATION_ANONYMOUS_REDIRECT_URL = '/accounts/login/'

ACCOUNT_LOGIN_ATTEMPTS_LIMIT = 5
ACCOUNT_LOGIN_ATTEMPTS_TIMEOUT = 300
ACCOUNT_LOGOUT_ON_PASSWORD_CHANGE = True
ACCOUNT_LOGOUT_REDIRECT_URL = '/'

REST_AUTH = {
    'USE_JWT': True,
    'JWT_AUTH_COOKIE': 'jwt-auth',
    'JWT_AUTH_REFRESH_COOKIE': 'jwt-refresh-token',
    'JWT_AUTH_HTTPONLY': False,
    'LOGIN_SERIALIZER': 'dj_rest_auth.serializers.LoginSerializer',
    'TOKEN_SERIALIZER': 'dj_rest_auth.serializers.TokenSerializer',
    'JWT_SERIALIZER': 'dj_rest_auth.serializers.JWTSerializer',
    'JWT_SERIALIZER_WITH_EXPIRATION': 'dj_rest_auth.serializers.JWTSerializerWithExpiration',
    'JWT_TOKEN_CLAIMS_SERIALIZER': 'rest_framework_simplejwt.serializers.TokenObtainPairSerializer',
    'USER_DETAILS_SERIALIZER': 'backend.api.serializers.user.UserDetailsSerializer',
    'PASSWORD_RESET_SERIALIZER': 'dj_rest_auth.serializers.PasswordResetSerializer',
    'PASSWORD_RESET_CONFIRM_SERIALIZER': 'dj_rest_auth.serializers.PasswordResetConfirmSerializer',
    'PASSWORD_CHANGE_SERIALIZER': 'dj_rest_auth.serializers.PasswordChangeSerializer',
    'REGISTER_SERIALIZER': 'backend.api.serializers.user.CustomRegisterSerializer',
    'REGISTER_PERMISSION_CLASSES': ('rest_framework.permissions.AllowAny',),
    'SESSION_LOGIN': False,
}


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

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

STATIC_URL = '/static/'

STATIC_ROOT = BASE_DIR / 'staticfiles'

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

SPECTACULAR_SETTINGS = {
    'TITLE': 'Netology Diploma API',
    'DESCRIPTION': 'Backend API для дипломного проекта',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'SCHEMA_PATH_PREFIX': r'/api',
    'COMPONENT_SPLIT_REQUEST': True,
    'SECURITY': [{'BearerAuth': []}],
    'SECURITY_SCHEMES': {
    'TokenAuth': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization'
    }
},
}

CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/0")
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Europe/Moscow'
CELERYD_POOL_RESTARTS = True
if sys.platform == "win32":
    CELERYD_POOL = "solo"

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = "webmaster@localhost"


BASE_URL = os.getenv('BASE_URL', 'http://localhost:8000')

SOCIAL_CALLBACK_URLS = {
    'github': f'{BASE_URL}/accounts/github/login/callback/',
    'google': f'{BASE_URL}/accounts/google/login/callback/',
    'yandex': f'{BASE_URL}/accounts/yandex/login/callback/',
    'vk': f'{BASE_URL}/accounts/vk/login/callback/',
}

from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,
    'JWK_URL': None,
    'LEEWAY': 0,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIMS': 'user_id',
    'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
    'TOKEN_USER_CLASS': 'rest_framework_simplejwt.models.TokenUser',
    'JTI_CLAIM': 'jti',
    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(minutes=5),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),
}