"""
Base Django settings for config project.
Derived by splitting the monolithic settings into base/dev/prod.
"""

from pathlib import Path
import os
from datetime import timedelta
import environ

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Environment
env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))
SECRET_KEY = env('SECRET_KEY', default='dev-please-change')

# Debug and hosts (overridden in dev/prod)
DEBUG = env.bool('DEBUG', default=True)
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['localhost','127.0.0.1'])

# Applications
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'comptables',
    'dossiers',
    'fiscal',
    'honoraires',
    'juridique',
    'api',
    'rest_framework',
    'rest_framework_simplejwt',
    'django_filters',
    'cabinet',
    'utilisateurs.apps.UtilisateursConfig',
    'crispy_forms',
    'crispy_bootstrap5',
    'reclamations.apps.ReclamationsConfig',
    'django.contrib.sites',
    'evenements',
    'django_celery_beat',
]
SITE_ID = 1

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

AUTH_USER_MODEL = 'utilisateurs.Utilisateur'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [Path(BASE_DIR) / 'templates', Path(BASE_DIR) / 'templates' / 'base'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            'libraries': {
                'crispy_forms_tags': 'crispy_forms.templatetags.crispy_forms_tags',
            }
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Email headers
EMAIL_HEADERS = {
    'X-Universite-Approved': 'true',
    'List-Unsubscribe': '<mailto:contact@cabinet-comptable.com>',
}

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('POSTGRES_DB', default='gestion_comptable_db'),
        'HOST': env('POSTGRES_HOST', default='localhost'),
        'PORT': env('POSTGRES_PORT', default='5432'),
        'USER': env('POSTGRES_USER', default='admin'),
        'PASSWORD': env('POSTGRES_PASSWORD', default='admin123'),
        'TEST': {
            'NAME': env('POSTGRES_TEST_DB', default='test_gestion_comptable_db'),
            'MIRROR': 'default'
        },
    }
}

# DRF
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_THROTTLE_CLASSES': (
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ),
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/day',
        'user': '1000/day',
    },
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
    ),
}

# Password validators
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

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static & Media
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Defaults
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Dates
DATE_INPUT_FORMATS = [
    '%Y-%m-%d',
    '%d/%m/%Y',
    '%d/%m/%y',
]
DATE_FORMAT = 'd/m/Y'
USE_L10N = False
LOGIN_REDIRECT_URL = '/dashboard/'
LOGIN_URL = '/accounts/login/'
LOGOUT_REDIRECT_URL = '/accounts/login/'

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'audit.log'),
            'formatter': 'verbose',
        },
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'mail_logs': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'mail.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
        'audit': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Email
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = env('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = env.int('EMAIL_PORT', default=587)
EMAIL_USE_TLS = env.bool('EMAIL_USE_TLS', default=True)
EMAIL_HOST_USER = env('EMAIL_HOST_USER', default='user@example.com')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', default='changeme')
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', default=EMAIL_HOST_USER)
ADMIN_EMAIL = env('ADMIN_EMAIL', default='admin@example.com')

# Celery
from celery.schedules import crontab
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_BEAT_SCHEDULE = {
    'send-greetings-every-day': {
        'task': 'evenements.tasks.envoyer_voeux_task',
        'schedule': timedelta(days=1),
        'args': (),
    },
    'send-tva-reminders': {
        'task': 'reclamations.tasks.send_rappel_tva_task',
        'schedule': crontab(hour=9, minute=0, day_of_week='1-5'),
    },
    'send-monthly-reports': {
        'task': 'comptables.tasks.send_monthly_reports_task',
        'schedule': crontab(day_of_month=1, hour=8),
    },
    'update-event-dates-annually': {
        'task': 'evenements.tasks_update_dates.update_event_dates_annually',
        'schedule': crontab(month_of_year=1, day_of_month=1, hour=0, minute=0),
    },
}
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'
EMAIL_USE_LOCALTIME = True

# Security (overridden in prod)
SESSION_COOKIE_SECURE = env.bool('SESSION_COOKIE_SECURE', default=False)
CSRF_COOKIE_SECURE = env.bool('CSRF_COOKIE_SECURE', default=False)
SECURE_SSL_REDIRECT = env.bool('SECURE_SSL_REDIRECT', default=False)
SECURE_HSTS_SECONDS = env.int('SECURE_HSTS_SECONDS', default=0)
SECURE_REFERRER_POLICY = 'same-origin'
X_FRAME_OPTIONS = 'DENY'
