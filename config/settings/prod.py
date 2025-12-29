"""
Production settings.
"""
from .base import *
import dj_database_url

DEBUG = False
# Hôtes autorisés (Plus flexible pour Render)
RENDER_EXTERNAL_HOSTNAME = env('RENDER_EXTERNAL_HOSTNAME', default=None)
ALLOWED_HOSTS = ['localhost', '127.0.0.1']
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)
ALLOWED_HOSTS.append('.onrender.com')

# Security hardening
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_REFERRER_POLICY = 'same-origin'
X_FRAME_OPTIONS = 'DENY'

# Static files
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Database
_db_url = env('DATABASE_URL', default=None)
if _db_url:
    DATABASES['default'] = dj_database_url.config(default=_db_url, conn_max_age=600, ssl_require=True)

# Celery Configuration
import os
REDIS_URL = os.environ.get('REDIS_URL') or os.environ.get('REDIS_INTERNAL_URL') or 'redis://redis-cache:6379/0'

CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
