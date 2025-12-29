"""
Production settings.
"""
from .base import *
import dj_database_url

DEBUG = False
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['localhost'])

# Security hardening
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_REFERRER_POLICY = 'same-origin'
X_FRAME_OPTIONS = 'DENY'

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

_db_url = env('DATABASE_URL', default=None)
if _db_url:
    DATABASES['default'] = dj_database_url.config(default=_db_url, conn_max_age=600, ssl_require=True)

# Celery Configuration
REDIS_URL = env('REDIS_URL', default=None)
if not REDIS_URL:
    # Fallback pour Render si la variable n'est pas liée via Blueprint
    REDIS_URL = env('REDIS_INTERNAL_URL', default='redis://localhost:6379/0')

CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
