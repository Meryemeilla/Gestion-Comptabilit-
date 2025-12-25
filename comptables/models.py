"""
Modèles Django et logique d’accès aux données.

Fichier: comptables/models.py
"""

# ==================== Imports ====================
from django.db import models
from django.core.validators import RegexValidator
from django.conf import settings
from django.db.models.signals import pre_save
from django.dispatch import receiver


# ==================== Classes ====================
class ComptableManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


class Comptable(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comptable_profile')

    
    """
    Modèle représentant un comptable du cabinet
    """
    matricule = models.CharField(
        max_length=20, 
        unique=True, 
        verbose_name="Matricule",
        help_text="Matricule unique du comptable",
        blank=True, # Allow blank for auto-generation
        null=True # Allow null for auto-generation
    )
    nom = models.CharField(
        max_length=100, 
        verbose_name="Nom"
    )
    prenom = models.CharField(
        max_length=100, 
        verbose_name="Prénom"
    )
    cnss = models.CharField(
        max_length=20, 
        blank=True, 
        null=True,
        verbose_name="Numéro CNSS",
        validators=[RegexValidator(
            regex=r'^\d{8,12}$',
            message='Le numéro CNSS doit contenir entre 8 et 12 chiffres'
        )]
    )
    tel = models.CharField(
        max_length=20, 
        blank=True, 
        null=True,
        verbose_name="Téléphone principal",
        validators=[RegexValidator(
            regex=r'^[\+]?[0-9\s\-\(\)]{10,20}$',
            message='Format de téléphone invalide'
        )]
    )
    tel_personnel = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="Téléphone personnel",
        validators=[RegexValidator(
            regex=r'^[\+]?[0-9\s\-\(\)]{10,20}$',
            message='Format de téléphone invalide'
        )]
    )
    email = models.EmailField(
        blank=True, 
        null=True,
        verbose_name="Email principal"
    )
    email_personnel = models.EmailField(
        blank=True, 
        null=True,
        verbose_name="Email personnel"
    )
    adresse = models.TextField(
        blank=True, 
        null=True,
        verbose_name="Adresse"
    )
    
    # Champs calculés automatiquement
    nbre_pm = models.IntegerField(
        default=0,
        verbose_name="Nombre de dossiers PM",
        help_text="Calculé automatiquement"
    )
    nbre_et = models.IntegerField(
        default=0,
        verbose_name="Nombre de dossiers ET",
        help_text="Calculé automatiquement"
    )
    nbre_personn = models.IntegerField(
        default=0,
        verbose_name="Nombre de personnes",
        help_text="Calculé automatiquement"
    )
    nbre_bureau = models.IntegerField(
        default=0,
        verbose_name="Nombre de bureaux",
        help_text="Calculé automatiquement"
    )
    
    # Métadonnées
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    actif = models.BooleanField(default=True, verbose_name="Actif")
    is_approved = models.BooleanField(default=False, verbose_name="Approuvé")
    is_deleted = models.BooleanField(default=False)

    objects = ComptableManager()
    all_objects = models.Manager()

    class Meta:
        verbose_name = "Comptable"
        verbose_name_plural = "Comptables"
        ordering = ['nom', 'prenom']

    def __str__(self):
        return f"{self.nom} {self.prenom} ({self.matricule})"

    @property
    def nom_complet(self):
        return f"{self.nom} {self.prenom}"

    def calculer_statistiques(self):
        """
        Calcule et met à jour les statistiques du comptable
        """
        from dossiers.models import Dossier
        
        dossiers = Dossier.objects.filter(comptable_traitant=self, actif=True, is_deleted=False)
        
        self.nbre_pm = dossiers.filter(forme_juridique__in=['SARL', 'SA', 'SNC', 'SCS', 'SCA', 'SASU', 'SAS']).count()
        self.nbre_et = dossiers.filter(forme_juridique__in=['EI', 'EIRL', 'AUTO', 'EURL', 'PP']).count()

        # Les autres calculs seront implémentés selon les besoins
        
        self.save(update_fields=['nbre_pm', 'nbre_et', 'nbre_personn', 'nbre_bureau'])

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('cabinet:comptable_detail', kwargs={'pk': self.pk})

from django.db.models.signals import post_delete
from django.dispatch import receiver

@receiver(post_delete, sender=Comptable)
# ==================== Fonctions ====================
def supprimer_utilisateur_associe(sender, instance, **kwargs):
        if instance.user:
            instance.user.delete()

@receiver(pre_save, sender=Comptable)
def generate_comptable_matricule(sender, instance, **kwargs):
    if not instance.matricule:
        # Generate a unique matricule, e.g., based on a sequence or timestamp
        # For simplicity, let's use a basic approach for now. 
        # In a real application, you might use a more robust sequence generator.
        last_comptable = Comptable.objects.all().order_by('-id').first()
        if last_comptable and last_comptable.matricule and last_comptable.matricule.startswith('COMPT-'):
            try:
                last_num = int(last_comptable.matricule.split('-')[1])
                new_num = last_num + 1
            except (ValueError, IndexError):
                new_num = 1
        else:
            new_num = 1
        instance.matricule = f'COMPT-{new_num:04d}'

        # Ensure uniqueness in case of race conditions (though unlikely with pre_save)
        while Comptable.objects.filter(matricule=instance.matricule).exists():
            new_num += 1
            instance.matricule = f'COMPT-{new_num:04d}'


