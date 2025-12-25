"""
Tâches asynchrones (Celery, planifications).

Fichier: evenements/tasks.py
"""

# ==================== Imports ====================
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from datetime import date
from .models import Evenement
from utilisateurs.models import Client
from comptables.models import Comptable
from cabinet.utils.email import EmailService
from .services import today_events, get_default_message, build_subject, build_message, get_celebrite_clients, get_celebrite_comptables

@shared_task
# ==================== Fonctions ====================
def envoyer_voeux_task():
    # Date sensible à la timezone Django
    email_service = EmailService()
    evenements_du_jour = today_events()

    for evenement in evenements_du_jour:
        default_msg = get_default_message(evenement)
        subject = build_subject(evenement)

        # Envoyer aux clients célébrités avec email
        for client in get_celebrite_clients():
            message = build_message(client.nom_complet, default_msg)
            email_service.send_email(
                to_emails=[client.email],
                subject=subject,
                message=message,
            )

        # Envoyer aux comptables célébrités avec email
        for comptable in get_celebrite_comptables():
            message = build_message(comptable.nom_complet, default_msg)
            email_service.send_email(
                to_emails=[comptable.email],
                subject=subject,
                message=message,
            )