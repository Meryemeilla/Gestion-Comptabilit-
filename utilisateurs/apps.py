"""
Configuration d’application Django.

Fichier: utilisateurs/apps.py
"""

# ==================== Imports ====================
from django.apps import AppConfig


     

# ==================== Classes ====================
class UtilisateursConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'utilisateurs'

    def ready(self):
        import utilisateurs.signals 
