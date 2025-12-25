"""
Configuration d’application Django.

Fichier: fiscal/apps.py
"""

# ==================== Imports ====================
from django.apps import AppConfig


# ==================== Classes ====================
class FiscalConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'fiscal'
