from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from .models import Dossier

@receiver(pre_save, sender=Dossier)
def sync_dossier_status(sender, instance, **kwargs):
    """
    Synchronise automatiquement le statut, l'activité et le soft delete en fonction du code du dossier.
    """
    if instance.code == 'D':
        instance.statut = 'DELAISSE'
        instance.actif = False
        instance.is_deleted = True
    elif instance.code == 'L':
        instance.statut = 'LIVRE'
        instance.actif = False
        instance.is_deleted = True
    elif instance.code == 'R':
        instance.statut = 'RADIE'
        instance.actif = False
        instance.is_deleted = True
    else:
        # On suppose que si ce n'est pas D, L ou R, c'est un dossier actif (P, S, F)
        instance.statut = 'EXISTANT'
        instance.actif = True
        instance.is_deleted = False

@receiver(post_save, sender=Dossier)
def on_dossier_save(sender, instance, created, **kwargs):
    """
    Actions à effectuer après la sauvegarde d'un dossier.
    """
    # 1. Mettre à jour les statistiques du comptable
    if instance.comptable_traitant:
        instance.comptable_traitant.calculer_statistiques()

    # 2. Synchroniser le nom de l'entreprise du client
    if instance.client and not instance.client.nom_entreprise:
        instance.client.nom_entreprise = instance.denomination
        instance.client.save()

@receiver(post_delete, sender=Dossier)
def on_dossier_delete(sender, instance, **kwargs):
    """
    Actions à effectuer après la suppression d'un dossier.
    """
    if instance.comptable_traitant:
        instance.comptable_traitant.calculer_statistiques()
