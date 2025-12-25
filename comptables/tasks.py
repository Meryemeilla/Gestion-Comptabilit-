"""
Tâches asynchrones (Celery, planifications).

Fichier: comptables/tasks.py
"""

# ==================== Imports ====================
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from datetime import date
from .models import Comptable
import logging

logger = logging.getLogger('audit')

@shared_task
# ==================== Fonctions ====================
def send_monthly_reports_task():
    """
    Tâche Celery pour envoyer les rapports mensuels aux comptables.
    Cette tâche est programmée pour s'exécuter le premier jour de chaque mois.
    """
    today = date.today()
    month_name = today.strftime("%B")
    year = today.year
    
    # Récupérer tous les comptables actifs
    comptables = Comptable.objects.all()
    
    for comptable in comptables:
        if not comptable.email:
            continue
            
        subject = f"Rapport mensuel - {month_name} {year}"
        message = f"""
        Cher(e) {comptable.nom_complet},
        
        Voici le rapport mensuel pour {month_name} {year}.
        
        Ce rapport contient un résumé des activités du mois précédent.
        
        Cordialement,
        L'équipe de gestion
        """
        
        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [comptable.email],
                fail_silently=False,
            )
            logger.info(f"Rapport mensuel envoyé à {comptable.email}")
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi du rapport mensuel à {comptable.email}: {str(e)}")
    
    return f"Rapports mensuels envoyés pour {month_name} {year}"