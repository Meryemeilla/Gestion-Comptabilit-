"""
Configuration d’application Django.

Fichier: juridique/apps.py
"""

# ==================== Imports ====================
from django.apps import AppConfig


# ==================== Classes ====================
class JuridiqueConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'juridique'
