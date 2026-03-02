import os
import logging
from datetime import timedelta
from pathlib import Path

from kombu import Queue, Exchange
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.django import DjangoIntegration

from libs.utils import get_env_variables_list
from django.templatetags.static import static # NOQA

# Environments
ENVIRONMENT_PRODUCTION = 'production'
ENVIRONMENT_DEVELOPMENT = 'dev'
ENVIRONMENT_LOCAL = 'local'

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

PROJECT_NAME = os.environ.get('PROJECT_NAME', 'Boilerplate')
ENVIRONMENT = os.environ.get('ENVIRONMENT', ENVIRONMENT_DEVELOPMENT)
RELEASE = os.environ.get('RELEASE', '0.1')

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', '')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = bool(int(os.environ.get('DEBUG', 0)))

if ENVIRONMENT == ENVIRONMENT_PRODUCTION:
    DEBUG = False

ALLOWED_HOSTS = get_env_variables_list(env_name='ALLOWED_HOSTS')
CORS_ALLOW_METHODS = get_env_variables_list(env_name='CORS_ALLOW_METHODS')
CORS_ALLOWED_ORIGINS = get_env_variables_list(env_name='CORS_ALLOWED_ORIGINS')
CSRF_TRUSTED_ORIGINS = get_env_variables_list(env_name='CSRF_TRUSTED_ORIGINS')


# Application definition

INSTALLED_APPS = [
    # --- Admin Dashboard ---
    "unfold",  # before django.contrib.admin
    "unfold.contrib.filters",  # optional, if special filters are needed
    "unfold.contrib.forms",  # optional, if special form elements are needed
    "unfold.contrib.inlines",  # optional, if special inlines are needed
    "unfold.contrib.import_export",  # optional, if django-import-export package is used
    "unfold.contrib.guardian",  # optional, if django-guardian package is used
    "unfold.contrib.simple_history",  # optional, if django-simple-history package is used
    # --- Admin Dashboard ---

    # Default apps
    "django.contrib.admin",
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Project apps
    'apps',
    # If needed create more than single app:
    # 'apps.examples',

    # Third party apps
    'debug_toolbar',
    'corsheaders',
    'rest_framework',
    'rest_framework_api_key',
    'storages',
    'drf_yasg',
    'nested_admin',



    'social_django',
]

# Enable/disable Celery-related features via environment variable
USE_CELERY = bool(int(os.environ.get('USE_CELERY', '0')))
if USE_CELERY:
    # Only include these apps when Celery is enabled to avoid import errors
    INSTALLED_APPS += [
        'django_celery_beat',
        'django_celery_results',
    ]

if DEBUG:
    import socket  # only if you haven't already imported this
    hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
    INTERNAL_IPS = [ip[: ip.rfind(".")] + ".1" for ip in ips] + ["127.0.0.1", "10.0.2.2"]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    "corsheaders.middleware.CorsMiddleware",
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'social_django.middleware.SocialAuthExceptionMiddleware',
]

ROOT_URLCONF = 'api.urls'

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
                'social_django.context_processors.backends',
                'social_django.context_processors.login_redirect',
            ],
        },
    },
]

WSGI_APPLICATION = 'settings.wsgi.application'

REST_FRAMEWORK = {
    'COERCE_DECIMAL_TO_STRING': False,
    'DEFAULT_PERMISSION_CLASSES': (
        # 'rest_framework.permissions.AllowAny',
        'rest_framework_api_key.permissions.HasAPIKey',

    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    )
}


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('POSTGRES_DB'),
        'USER': os.environ.get('POSTGRES_USER'),
        'PASSWORD': os.environ.get('POSTGRES_PASS'),
        'HOST': os.environ.get('POSTGRES_HOST'),
        'PORT': int(os.environ.get('POSTGRES_PORT')),
    }
}

# authentik
# https://python-social-auth.readthedocs.io/en/latest/configuration/django.html

AUTHENTICATION_BACKENDS = [
    'social_core.backends.open_id_connect.OpenIdConnectAuth',
    'django.contrib.auth.backends.ModelBackend',
]

if USE_SOCIAL := bool(int(os.environ.get('USE_SOCIAL', '0'))):
    SOCIAL_AUTH_URL_NAMESPACE = 'social'

    SOCIAL_AUTH_OIDC_OIDC_ENDPOINT = os.environ.get('SOCIAL_AUTH_OIDC_OIDC_ENDPOINT', '')
    SOCIAL_AUTH_OIDC_KEY = os.environ.get('SOCIAL_AUTH_OIDC_KEY', '')
    SOCIAL_AUTH_OIDC_SECRET = os.environ.get('SOCIAL_AUTH_OIDC_SECRET', '')

    SOCIAL_AUTH_JSONFIELD_ENABLED = True

    if DEBUG:
        SOCIAL_AUTH_REDIRECT_IS_HTTPS = False
        LOGIN_REDIRECT_URL = '/admin/'
        LOGOUT_REDIRECT_URL = '/admin/login/'
        LOGIN_URL = '/oauth/login/oidc/'
    else:
        SOCIAL_AUTH_REDIRECT_IS_HTTPS = True
        LOGIN_REDIRECT_URL = '/'
        LOGOUT_REDIRECT_URL = '/'
        LOGIN_URL = '/oauth/login/oidc/'

    SOCIAL_AUTH_PIPELINE = (
        # "social_core.pipeline.debug.debug",

        "social_core.pipeline.social_auth.social_details",
        "social_core.pipeline.social_auth.social_uid",
        "social_core.pipeline.social_auth.auth_allowed",
        "social_core.pipeline.social_auth.social_user",
        "social_core.pipeline.user.get_username",
        "social_core.pipeline.mail.mail_validation",
        # "social_core.pipeline.user.create_user",
        'apps.core.oauth.pipeline.create_user',
        "social_core.pipeline.social_auth.associate_user",
        "social_core.pipeline.social_auth.load_extra_data",
        # "social_core.pipeline.user.user_details",
        'apps.core.oauth.pipeline.set_user_permissions',
    )

# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

DJANGO_SUPERUSER_LOGIN = os.environ.get('DJANGO_SUPERUSER_LOGIN', 'admin')
DJANGO_SUPERUSER_EMAIL = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@admin.com')
DJANGO_SUPERUSER_PASSWORD = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'admin')


# Unfold settings
# https://unfoldadmin.com/docs/installation/quickstart/

COLOR_SCHEME = {
    "50": "255 247 237",   # Lightest
    "100": "255 237 213",
    "200": "254 215 170",
    "300": "253 186 116",
    "400": "251 146 60",
    "500": "249 115 22",   # Primary orange
    "600": "234 88 12",
    "700": "194 65 12",
    "800": "154 52 18",
    "900": "124 45 18",    # Darkest
}

SLATE_PALETTE = {
    "50": "248 250 252",   # Lightest
    "100": "241 245 249",
    "200": "226 232 240",
    "300": "203 213 225",
    "400": "148 163 184",
    "500": "100 116 139",  # Primary slate
    "600": "71 85 105",
    "700": "51 65 85",
    "800": "30 41 59",
    "900": "15 23 42",     # Darkest
}

UNFOLD = {
    # ... other settings ...
    "COLORS": {
        "base": SLATE_PALETTE,
        "primary": COLOR_SCHEME,
        # You can also customize other color categories if needed
    },
    "BORDER_RADIUS": "10px",
    # Customize sidebar navigation - group Celery models
    # "SIDEBAR": {
    #     "show_search": True,
    #     "show_all_applications": True,
    #     "navigation": [
    #         {
    #             "title": "Celery",
    #             "separator": True,
    #             "items": [
    #                 {
    #                     "title": "Celery Dashboard",
    #                     "icon": "dashboard",
    #                     "link": lambda request: "/admin/celery-dashboard/",
    #                 },
    #                 {
    #                     "title": "Periodic Tasks",
    #                     "icon": "schedule",
    #                     "link": lambda request: "/admin/django_celery_beat/periodictask/",
    #                 },
    #                 {
    #                     "title": "Task Results",
    #                     "icon": "task_alt",
    #                     "link": lambda request: "/admin/django_celery_results/taskresult/",
    #                 },
    #                 {
    #                     "title": "Interval Schedules",
    #                     "icon": "update",
    #                     "link": lambda request: "/admin/django_celery_beat/intervalschedule/",
    #                 },
    #                 {
    #                     "title": "Crontab Schedules",
    #                     "icon": "schedule",
    #                     "link": lambda request: "/admin/django_celery_beat/crontabschedule/",
    #                 },
    #                 {
    #                     "title": "Clocked Schedules",
    #                     "icon": "access_time",
    #                     "link": lambda request: "/admin/django_celery_beat/clockedschedule/",
    #                 },
    #                 {
    #                     "title": "Solar Schedules",
    #                     "icon": "wb_sunny",
    #                     "link": lambda request: "/admin/django_celery_beat/solarschedule/",
    #                 },
    #             ],
    #         },
    #     ],
    # },
    # Additional configurations...
}


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

# S3
USE_S3 = bool(int(os.environ.get('USE_S3')))
if USE_S3:
    # General settings
    S3_ENDPOINT_URL = os.environ.get('S3_ENDPOINT_URL')  # URL of your S3-compatible server
    S3_ACCESS_KEY_ID = os.environ.get('S3_ACCESS_KEY_ID')
    S3_SECRET_ACCESS_KEY = os.environ.get('S3_SECRET_ACCESS_KEY')
    S3_STORAGE_BUCKET_NAME = os.environ.get('S3_STORAGE_BUCKET_NAME')

    endpoint_no_scheme = (
        S3_ENDPOINT_URL.replace("https://", "").replace("http://", "")
    )

    # Custom domain can be left only for media
    S3_CUSTOM_DOMAIN = os.environ.get(
        "S3_CUSTOM_DOMAIN",
        f"{endpoint_no_scheme}/{S3_STORAGE_BUCKET_NAME}",
    )

    MEDIA_URL = f"https://{S3_CUSTOM_DOMAIN}/media/"
    # You can leave STATIC_URL as is, {% static %} will get URL from storage.url()
    STATIC_URL = "/static/"  # the value here is almost irrelevant

    AWS_S3_ENDPOINT_URL = S3_ENDPOINT_URL
    AWS_ACCESS_KEY_ID = S3_ACCESS_KEY_ID
    AWS_SECRET_ACCESS_KEY = S3_SECRET_ACCESS_KEY
    AWS_STORAGE_BUCKET_NAME = S3_STORAGE_BUCKET_NAME
    AWS_S3_CUSTOM_DOMAIN = None  # important: globally disable custom_domain
    AWS_S3_OBJECT_PARAMETERS = {
        "CacheControl": "max-age=86400",
    }

    AWS_QUERYSTRING_AUTH = True
    AWS_QUERYSTRING_EXPIRE = 3600

    STORAGES = {
        "default": {
            "BACKEND": "settings.storages.MediaStorage",
        },
        "staticfiles": {
            "BACKEND": "settings.storages.StaticStorage",
        },
    }

else:
    STATIC_DIR = 'backend-static'
    STATIC_URL = f'/api/{STATIC_DIR}/'
    STATIC_ROOT = os.path.join(BASE_DIR, STATIC_DIR)

    MEDIA_DIR = 'media'
    MEDIA_URL = f'/api/{MEDIA_DIR}/'
    MEDIA_ROOT = os.path.join(BASE_DIR, MEDIA_DIR)

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# DRF yasg settings (api documentation)
# https://drf-yasg.readthedocs.io/en/stable/settings.html

SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header'
        }
    },
    'REFETCH_SCHEMA_WITH_AUTH': True,
    'USE_SESSION_AUTH': False,
    'PERSIST_AUTH': True,
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    "formatters": {
        "verbose": {
            "format": "[{asctime} {levelname} {pathname}.{funcName}:{lineno}] {message}",
            "style": "{",
        },
        "simple": {
            "format": "[{asctime} {levelname} {funcName}:{lineno}] {message}",
            "style": "{",
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            "formatter": "verbose",
        },
    },
    'loggers': {
        '': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
        },
    },
}

SENTRY_DSN = os.environ.get('SENTRY_DSN', None)
SENTRY_ENVIRONMENT = ENVIRONMENT
SENTRY_RELEASE = RELEASE

sentry_sdk.init(
    dsn=SENTRY_DSN,
    environment=SENTRY_ENVIRONMENT,
    release=SENTRY_RELEASE,
    traces_sample_rate=1.0,
    profiles_sample_rate=1.0,
    integrations=[
        DjangoIntegration(
            transaction_style='url',
            middleware_spans=True,
            signals_spans=False,
            cache_spans=False,
        ),
        LoggingIntegration(
            level=logging.INFO,
            event_level=logging.WARNING,
        ),
    ]
)


if USE_CELERY := bool(int(os.environ.get('USE_CELERY', '0'))):
    CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://redis:6379')
    CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://redis:6379')
    CELERY_TASK_TRACK_STARTED = True
    CELERY_TASK_TIME_LIMIT = int(os.environ.get('CELERY_TASK_TIME_LIMIT_MIN', 5)) * 60
    # Fix deprecation warning for Celery 6.0+
    CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True

    CELERY_DEFAULT_QUEUE_NAME = 'default'

    CELERY_QUEUES = [
        Queue(
            CELERY_DEFAULT_QUEUE_NAME,
            Exchange(CELERY_DEFAULT_QUEUE_NAME),
            routing_key=CELERY_DEFAULT_QUEUE_NAME,
        ),
    ]

    CELERY_IMPORTS = (
        'apps.posts.tasks',
    )

    CELERY_TASK_DEFAULT_QUEUE = CELERY_DEFAULT_QUEUE_NAME

    CELERY_ROUTES = dict()
    CELERY_BEAT_SCHEDULE = {
        'twitter-update-followers-stats': {
            'task': 'apps.stats.twitter.tasks.count_followers_stats',
            'schedule': timedelta(seconds=int(os.environ.get('SCHEDULE_ENV', 60))),
            'options': {
                'queue': CELERY_TASK_DEFAULT_QUEUE,
            },
        }
    }

    # Scheduled tasks
    # Create boolean SWITCHER_ENV to enable/disable tasks
    # Create int SCHEDULE_ENV to define schedule for task in seconds
    # if bool(int(os.environ.get('SWITCHER_ENV', '0'))):
    #     CELERY_BEAT_SCHEDULE.update(
    #         {
    #             'task-name': {
    #                 'task': 'apps.app.tasks.task_function',
    #                 'schedule': timedelta(seconds=int(os.environ.get('SCHEDULE_ENV', 60))),
    #                 'options': {
    #                     'queue': CELERY_TASK_DEFAULT_QUEUE,
    #                 },
    #             },
    #         }
    #     )
