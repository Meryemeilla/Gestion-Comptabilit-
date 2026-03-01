"""
Tâches asynchrones (Celery, planifications).

Fichier: reclamations/tasks.py
"""

# ==================== Imports ====================
from celery import shared_task
from celery.utils.log import get_task_logger
from cabinet.utils.email import EmailService
from dossiers.models import Dossier
from datetime import datetime
from reclamations.models import Reclamation
import logging
logger = logging.getLogger(__name__)

@shared_task
# ==================== Fonctions ====================
def send_reclamation_email_task(reclamation_id):
    reclamation = Reclamation.objects.get(id=reclamation_id)
    email_service = EmailService()
    result = email_service.send_notification_reclamation(reclamation)
    if not result:
        # Tu peux logger une erreur si besoin
        print(f"Erreur lors de l'envoi de l'email pour la réclamation {reclamation_id}")
    return result
    
@shared_task
def send_rappel_tva_task():
    """Tâche programmée pour les rappels TVA"""
    dossiers = Dossier.objects.filter(
        statut_fiscal='EN_RETARD',
        dernier_rappel_tva__lt=datetime.now().date()  # Evite les rappels multiples
    )
    
    if not dossiers.exists():
        logger.info("Aucun dossier TVA en retard à notifier")
        return True
        
    service = EmailService()
    result = service.send_rappel_tva(dossiers)
    
    if result:
        # Marque les dossiers comme notifiés
        dossiers.update(dernier_rappel_tva=datetime.now().date())
    
    return result