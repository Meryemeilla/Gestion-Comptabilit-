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
