"""
Configuration d’application Django.

Fichier: comptables/apps.py
"""

# ==================== Imports ====================
from django.apps import AppConfig


# ==================== Classes ====================
class ComptablesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'comptables'
