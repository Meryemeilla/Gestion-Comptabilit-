from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Utilisateur, Client
from .tasks import envoyer_email_creation_client  # ⬅️ importe la tâche Celery

@receiver(post_save, sender=Client)
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
        envoyer_email_creation_client.delay(
            to_email=instance.email,
            password=raw_password,
            nom_client=instance.nom,
            login_url='http://127.0.0.1:8000/accounts/login/?next=/'
        )
