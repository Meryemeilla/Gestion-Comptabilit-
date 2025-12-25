"""
Services métier réutilisables et testables.

Fichier: evenements/services.py
"""

# ==================== Imports ====================
from django.utils import timezone
from utilisateurs.models import Client
from comptables.models import Comptable
from .models import Evenement


# ==================== Fonctions ====================
def get_default_message(evenement: Evenement) -> str:
    """
    Retourne le message de vœux par défaut pour l'événement.
    Utilise Evenement.DEFAULT_MESSAGES, sinon repli sur evenement.message.
    """
    return Evenement.DEFAULT_MESSAGES.get(evenement.nom) or getattr(evenement, 'message', '') or ''


def build_subject(evenement: Evenement) -> str:
    """Construit un sujet d'email cohérent sans doublon."""
    return f"Vœux de {evenement.nom}"


def build_message(nom_complet: str, default_msg: str) -> str:
    """Construit le corps du message personnalisé par destinataire."""
    return f"Cher {nom_complet}, {default_msg}".strip()


def get_celebrite_clients():
    """Retourne les clients marqués comme célébrités avec email renseigné."""
    return Client.objects.filter(user__est_celebrite=True, email__isnull=False)


def get_celebrite_comptables():
    """Retourne les comptables marqués comme célébrités avec email renseigné."""
    return Comptable.objects.filter(user__est_celebrite=True, email__isnull=False)


def today_events():
    """Retourne les événements actifs du jour (timezone locale)."""
    today = timezone.localdate()
    return Evenement.objects.filter(date=today, actif=True)