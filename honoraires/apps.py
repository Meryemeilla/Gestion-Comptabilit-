"""
Configuration d’application Django.

Fichier: honoraires/apps.py
"""

# ==================== Imports ====================
from django.apps import AppConfig


# ==================== Classes ====================
class HonorairesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'honoraires'
