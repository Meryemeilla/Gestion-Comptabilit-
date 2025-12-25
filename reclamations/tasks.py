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
from cabinet.utils.email import EmailService 

logger =  logging.getLogger(__name__)

# @shared_task(bind=True, max_retries=3)
# def send_reclamation_email_task(self, reclamation_id):
#     """Tâche pour envoyer les notifications de réclamation avec retry"""
#     from reclamations.models import Reclamation
    
#     try:
#         reclamation = Reclamation.objects.get(id=reclamation_id)
#         service = EmailService()
#         result = service.send_notification_reclamation(reclamation)
        
#         if not result:
#             logger.error(f"Échec envoi email réclamation ID {reclamation_id}")
#             self.retry(countdown=60 * 5)  # Réessaye après 5 minutes
        
#         return result
        
#     except Reclamation.DoesNotExist as e:
#         logger.error(f"Réclamation non trouvée: {reclamation_id}")
#         raise self.retry(exc=e, countdown=60 * 10)  # Réessaye après 10 minutes


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
        tva_en_retard=True,
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