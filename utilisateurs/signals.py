"""
Signaux et hooks (post_save, etc.).

Fichier: utilisateurs/signals.py
"""

# ==================== Imports ====================
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Utilisateur, Client
from .tasks import envoyer_email_creation_client  # ⬅️ importe la tâche Celery

@receiver(post_save, sender=Client)
# ==================== Fonctions ====================
def creer_utilisateur_pour_client(sender, instance, created, **kwargs):
    if created and not instance.user:
        raw_password = getattr(instance, 'plain_password', None)

        if not raw_password:
            return

        user = Utilisateur.objects.create_user(
            username=instance.email,
            email=instance.email,
            password=raw_password,
            role='client'
        )
        instance.user = user
        instance.save()

        print("Tâche Celery appelée pour l'email")
        
        # On tente de récupérer l'URL de base de l'environnement ou on utilise le domaine par défaut
        base_url = os.environ.get('RENDER_EXTERNAL_URL', 'https://gestion-comptabilite.onrender.com')
        login_url = f"{base_url.rstrip('/')}/accounts/login/"

        try:
            envoyer_email_creation_client.delay(
                prenom=user.first_name or instance.contact_personne,
                username=user.username,
                to_email=instance.email,
                password=raw_password,
                nom_client=instance.nom_entreprise or instance.contact_personne,
                login_url=login_url
            )
        except Exception as e:
            print(f"Erreur signal Celery: {e}")
