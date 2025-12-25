"""
Modèles Django et logique d’accès aux données.

Fichier: reclamations/models.py
"""

# ==================== Imports ====================
from django.db import models
from dossiers.models import Dossier
from django.conf import settings

# ==================== Classes ====================
class ReclamationManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


class Reclamation(models.Model):
    """
    Modèle pour la gestion des réclamations
    """
    dossier = models.ForeignKey(
        Dossier,
        on_delete=models.CASCADE,
        related_name='reclamations',
        verbose_name="Dossier"
    )
    code = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        null=True,
        help_text="Code métier unique pour identifier la réclamation"
    )
    document = models.FileField(upload_to='reclamations/documents/', blank=True, null=True, verbose_name="Document joint")
    type_reclamation = models.CharField(
        max_length=100,
        verbose_name="Type de réclamation"
    )
    date_reception = models.DateField(
        verbose_name="Date de réception"
    )
    reponse = models.TextField(
        blank=True,
        null=True,
        verbose_name="Réponse"
    )
    suivi = models.TextField(
        blank=True,
        null=True,
        verbose_name="Suivi"
    )
    remarque = models.TextField(
        blank=True,
        null=True,
        verbose_name="Remarques"
    )
    destinataire = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reclamations_recues',
        verbose_name='Destinataire',
        null=True,
        blank=True
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reclamations_envoyees',
        
    )
    
    # Classement
    CLASSEMENT_CHOICES = [
        ('EN_COURS', 'En cours'),
        ('RESOLU', 'Résolu'),
        ('CLOS', 'Clos'),
        ('REPORTE', 'Reporté'),
        ('ANNULE', 'Annulé'),
    ]
    classement = models.CharField(
        max_length=20,
        choices=CLASSEMENT_CHOICES,
        default='EN_COURS',
        verbose_name="Classement"
    )
    
    # Priorité
    PRIORITE_CHOICES = [
        ('BASSE', 'Basse'),
        ('NORMALE', 'Normale'),
        ('HAUTE', 'Haute'),
        ('URGENTE', 'Urgente'),
    ]
    priorite = models.CharField(
        max_length=20,
        choices=PRIORITE_CHOICES,
        default='NORMALE',
        verbose_name="Priorité"
    )
    
    # Métadonnées
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False, verbose_name="Supprimé")

    objects = ReclamationManager()
    all_objects = models.Manager()

    class Meta:
        verbose_name = "Réclamation"
        verbose_name_plural = "Réclamations"
        ordering = ['-date_reception']

    def __str__(self):
        return f"Réclamation {self.type_reclamation} - {self.dossier.denomination}"

    def delete(self, *args, **kwargs):
        self.is_deleted = True
        self.save()

    def restore(self, *args, **kwargs):
        self.is_deleted = False
        self.save()
