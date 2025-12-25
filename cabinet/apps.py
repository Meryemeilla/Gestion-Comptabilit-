"""
Configuration d’application Django.

Fichier: cabinet/apps.py
"""

# ==================== Imports ====================
from django.apps import AppConfig


# ==================== Classes ====================
class CabinetConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'cabinet'
