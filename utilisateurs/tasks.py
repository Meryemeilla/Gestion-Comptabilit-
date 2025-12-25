"""
Tâches asynchrones (Celery, planifications).

Fichier: utilisateurs/tasks.py
"""

# ==================== Imports ====================
from celery import shared_task
from cabinet.utils.email import EmailService
from utilisateurs.models import Utilisateur
from django.conf import settings
@shared_task
# ==================== Fonctions ====================
def envoyer_email_creation_client(prenom, username, to_email, password, nom_client, login_url):

    print(f" Envoi de l’email à {to_email}")
    EmailService().send_template_email(
        to_emails=[to_email],
        subject="Votre compte client a été créé",
        template_name="bienvenue_client",
        context={
            'prenom': prenom,
            'username': username,
            'email': to_email,
            'password': password,
            'nom_client': nom_client,
            'login_url': login_url,
        }
    )

@shared_task
def envoyer_email_nouveau_client(user_id):
    try:
        user = Utilisateur.objects.get(id=user_id)
    except Utilisateur.DoesNotExist:
        return

    # URL statique ou générée dynamiquement
    from django.urls import reverse
    from django.contrib.sites.models import Site

    current_site = Site.objects.get_current()
    liste_clients_url = f"https://{current_site.domain}{reverse('cabinet:liste_clients')}"

    EmailService().send_template_email(
        to_emails=[settings.ADMIN_EMAIL],
        subject="Nouveau client inscrit",
        template_name="nouveau_client",
        context={
            "user": user,
            "liste_clients_url": liste_clients_url
        }
    )

@shared_task
def envoyer_email_creation_comptable(user_id, password_plain=None):
    from django.contrib.sites.models import Site
    from django.urls import reverse

    try:
        user = Utilisateur.objects.get(id=user_id)
    except Utilisateur.DoesNotExist:
        return

    current_site = Site.objects.get_current()
    espace_comptable_url = f"https://{current_site.domain}{reverse('cabinet:dashboard')}"

    EmailService().send_template_email(
        to_emails=[user.email],
        subject="Votre compte comptable a été créé",
        template_name="compte_comptable_cree",
        context={
            'prenom': user.first_name,
            'username': user.username,
            'email': user.email,
            'password': password_plain,
            'espace_comptable_url': espace_comptable_url
        }
    )
