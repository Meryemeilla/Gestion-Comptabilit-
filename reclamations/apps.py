"""
Configuration d’application Django.

Fichier: reclamations/apps.py
"""

# ==================== Imports ====================
from django.apps import AppConfig


# ==================== Classes ====================
class ReclamationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'reclamations'

    def ready(self):
        import reclamations.signals
