"""
Configuration d’application Django.

Fichier: dossiers/apps.py
"""

# ==================== Imports ====================
from django.apps import AppConfig


# ==================== Classes ====================
class DossiersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'dossiers'
