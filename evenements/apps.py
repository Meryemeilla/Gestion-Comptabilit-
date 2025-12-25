"""
Configuration d’application Django.

Fichier: evenements/apps.py
"""

# ==================== Imports ====================
from django.apps import AppConfig


# ==================== Classes ====================
class EvenementsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'evenements'
