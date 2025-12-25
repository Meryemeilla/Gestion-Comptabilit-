"""
Module applicatif.

Fichier: test_email.py
"""

# ==================== Imports ====================
import os
import django

# Configurer l'environnement Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# Importer la fonction de tâche
from evenements.tasks import envoyer_voeux_task

# Exécuter la fonction directement
if __name__ == "__main__":
    print("Début du test d'envoi d'e-mails de vœux...")
    envoyer_voeux_task()
    print("Test terminé. Vérifiez les e-mails dans la console ci-dessus.")