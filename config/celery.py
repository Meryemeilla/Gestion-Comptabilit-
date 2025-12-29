"""
Module applicatif.

Fichier: config/celery.py
"""

# ==================== Imports ====================
from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Indique à Django les settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.prod')

app = Celery('gestion_comptabilite')

# Charge les settings CELERY_ depuis Django
app.config_from_object('django.conf:settings', namespace='CELERY')

# Découvre les tâches dans tous les fichiers tasks.py
app.autodiscover_tasks()

@app.task(bind=True)
# ==================== Fonctions ====================
def debug_task(self):
    print(f'Requête Celery: {self.request!r}')

if __name__ == '__main__':
    app.start()
