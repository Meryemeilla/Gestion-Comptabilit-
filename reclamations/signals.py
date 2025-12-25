"""
Signaux et hooks (post_save, etc.).

Fichier: reclamations/signals.py
"""

# ==================== Imports ====================
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Reclamation
from .tasks import send_reclamation_email_task
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Reclamation)
# ==================== Fonctions ====================
def envoyer_email_reclamation(sender, instance, created, **kwargs):
    if created:
        print(" Signal déclenché : nouvelle réclamation")
        try:
            send_reclamation_email_task.delay(instance.id)
            print(" Tâche email de réclamation créée")
        except Exception as e:
            print(f" Erreur d'envoi de tâche : {e}")



