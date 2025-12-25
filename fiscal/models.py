"""
Modèles Django et logique d’accès aux données.

Fichier: fiscal/models.py
"""

# ==================== Imports ====================
from django.db import models
from django.db.models.query import QuerySet
from django.core.validators import MinValueValidator
from decimal import Decimal
from dossiers.models import Dossier
import random
import string
from cabinet.soft_delete_models import SoftDeleteModel, SoftDeleteManager


# ==================== Classes ====================
class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)

    def all_with_deleted(self):
        return super().get_queryset()

    def deleted_set(self):
        return super().get_queryset().filter(is_deleted=True)


class SoftDeleteModel(models.Model):
    is_deleted = models.BooleanField(default=False, verbose_name="Supprimé")

    objects = SoftDeleteManager()
    all_objects = models.Manager()

    class Meta:
        abstract = True

    def soft_delete(self):
        self.is_deleted = True
        self.save()

    def restore(self):
        self.is_deleted = False
        self.save()


class SuiviTVA(SoftDeleteModel):
    """
    Modèle pour le suivi des déclarations TVA mensuelles et trimestrielles
    """
    dossier = models.ForeignKey(
        Dossier,
        on_delete=models.CASCADE,
        related_name='suivis_tva',
        verbose_name="Dossier"
    )
    code = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        null=True,
       
    )
    annee = models.IntegerField(
        verbose_name="Année"
    )
    
    # Suivi mensuel
    jan = models.BooleanField(default=False, verbose_name="Janvier")
    fev = models.BooleanField(default=False, verbose_name="Février")
    mars = models.BooleanField(default=False, verbose_name="Mars")
    avril = models.BooleanField(default=False, verbose_name="Avril")
    mai = models.BooleanField(default=False, verbose_name="Mai")
    juin = models.BooleanField(default=False, verbose_name="Juin")
    juillet = models.BooleanField(default=False, verbose_name="Juillet")
    aout = models.BooleanField(default=False, verbose_name="Août")
    sep = models.BooleanField(default=False, verbose_name="Septembre")
    oct = models.BooleanField(default=False, verbose_name="Octobre")
    nov = models.BooleanField(default=False, verbose_name="Novembre")
    dec = models.BooleanField(default=False, verbose_name="Décembre")
    
    # Suivi trimestriel
    t1 = models.BooleanField(default=False, verbose_name="1er trimestre")
    t2 = models.BooleanField(default=False, verbose_name="2ème trimestre")
    t3 = models.BooleanField(default=False, verbose_name="3ème trimestre")
    t4 = models.BooleanField(default=False, verbose_name="4ème trimestre")
    
    
    # # Métadonnées
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    # is_deleted = models.BooleanField(default=False, verbose_name="Supprimé")
    # is_deleted = models.BooleanField(default=False, verbose_name="Supprimé")
    # is_deleted = models.BooleanField(default=False, verbose_name="Supprimé")

   
    class Meta(SoftDeleteModel.Meta):
        verbose_name = "Suivi TVA"
        verbose_name_plural = "Suivis TVA"
        unique_together = ['dossier', 'annee']
        ordering = ['-annee']

    def __str__(self):
        return f"Suivi TVA {self.annee} - {self.dossier.denomination}"

    @property
    def pourcentage_mensuel_complete(self):
        """Calcule le pourcentage de déclarations mensuelles complétées"""
        mois = [self.jan, self.fev, self.mars, self.avril, self.mai, self.juin,
                self.juillet, self.aout, self.sep, self.oct, self.nov, self.dec]
        return (sum(mois) / 12) * 100

    @property
    def pourcentage_trimestriel_complete(self):
        """Calcule le pourcentage de déclarations trimestrielles complétées"""
        trimestres = [self.t1, self.t2, self.t3, self.t4]
        return (sum(trimestres) / 4) * 100

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = self.generer_code_unique()
        super().save(*args, **kwargs)

    def generer_code_unique(self):
        while True:
            code = random.choice(string.ascii_uppercase) + \
                   ''.join(random.choices(string.digits, k=3)) + \
                   random.choice(string.ascii_uppercase)
            if not self.__class__.objects.filter(code=code).exists():
                return code
    
    

# from django.db import models
# from django.core.validators import MinValueValidator
# from django.utils import timezone

# class Paiement(models.Model):
#     """
#     Modèle pour enregistrer les paiements liés aux déclarations TVA
#     """
#     TYPE_CHOICES = [
#         ('TVA', 'Paiement TVA'),
#         ('PENALITE', 'Pénalités de retard'),
#         ('REGULARISATION', 'Régularisation'),
#     ]

#     MODE_CHOICES = [
#         ('VIREMENT', 'Virement bancaire'),
#         ('CHEQUE', 'Chèque'),
#         ('ESPECES', 'Espèces'),
#         ('AUTRE', 'Autre moyen'),
#     ]

#     # Relation avec le suivi TVA
#     suivi_tva = models.ForeignKey(
#         'SuiviTVA',
#         on_delete=models.CASCADE,
#         related_name='paiements',
#         verbose_name="Déclaration associée"
#     )

#     # Informations de base
#     type_paiement = models.CharField(
#         max_length=20,
#         choices=TYPE_CHOICES,
#         default='TVA',
#         verbose_name="Type de paiement"
#     )
#     montant = models.DecimalField(
#         max_digits=12,
#         decimal_places=2,
#         validators=[MinValueValidator(0)],
#         verbose_name="Montant payé"
#     )
#     date_paiement = models.DateField(
#         default=timezone.now,
#         verbose_name="Date de paiement"
#     )
#     mode_paiement = models.CharField(
#         max_length=20,
#         choices=MODE_CHOICES,
#         default='VIREMENT',
#         verbose_name="Mode de paiement"
#     )

#     # Références
#     reference = models.CharField(
#         max_length=50,
#         blank=True,
#         null=True,
#         verbose_name="Référence paiement"
#     )
#     numero_quittance = models.CharField(
#         max_length=50,
#         blank=True,
#         null=True,
#         verbose_name="Numéro de quittance"
#     )

#     # Fichiers justificatifs
#     justificatif = models.FileField(
#         upload_to='paiements/tva/justificatifs/',
#         null=True,
#         blank=True,
#         verbose_name="Justificatif de paiement"
#     )

#     # Métadonnées
#     date_creation = models.DateTimeField(auto_now_add=True)
#     date_modification = models.DateTimeField(auto_now=True)
#     created_by = models.ForeignKey(
#         'auth.User',
#         on_delete=models.SET_NULL,
#         null=True,
#         related_name='paiements_crees'
#     )

#     class Meta:
#         verbose_name = "Paiement TVA"
#         verbose_name_plural = "Paiements TVA"
#         ordering = ['-date_paiement']
#         constraints = [
#             models.UniqueConstraint(
#                 fields=['suivi_tva', 'numero_quittance'],
#                 name='unique_quittance_per_declaration',
#                 condition=models.Q(numero_quittance__isnull=False)
#             )
#         ]

#     def __str__(self):
#         return f"Paiement {self.type_paiement} - {self.montant} MAD - {self.date_paiement}"

#     @property
#     def est_en_retard(self):
#         """Vérifie si le paiement est en retard par rapport à la période déclarée"""
#         if not hasattr(self, '_est_en_retard'):
#             dernier_jour = self.get_dernier_jour_paiement()
#             self._est_en_retard = (self.date_paiement > dernier_jour) if dernier_jour else False
#         return self._est_en_retard

#     def get_dernier_jour_paiement(self):
#         """Calcule la date limite de paiement selon la période TVA"""
#         from dateutil.relativedelta import relativedelta
        
#         if self.suivi_tva.t1 and self.type_paiement == 'TVA':
#             return timezone.datetime(self.suivi_tva.annee, 4, 30).date()
#         # Ajoutez les autres conditions pour les trimestres/mois
        
#         return None

#     def save(self, *args, **kwargs):
#         """Génération automatique de la référence si vide"""
#         if not self.reference:
#             self.reference = f"PAY-TV-{self.suivi_tva.annee}-{self.pk or 'NEW'}"
#         super().save(*args, **kwargs)

class Acompte(SoftDeleteModel):
    """
    Modèle pour le suivi des acomptes
    """
    dossier = models.ForeignKey(
        Dossier,
        on_delete=models.CASCADE,
        related_name='acomptes',
        verbose_name="Dossier"
    )
    code = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        null=True,
        
    )
    annee = models.IntegerField(
        verbose_name="Année"
    )
    montant = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        blank=True,  
        null=True,  
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="Montant total"
    )
    regularisation = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Régularisation"
    )
    
    # Acomptes
    a1 = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="1er acompte"
    )
    a2 = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="2ème acompte"
    )
    a3 = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="3ème acompte"
    )
    a4 = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="4ème acompte"
    )
    is_montant = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="Montant IS"
    )
    
    # Métadonnées
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    # is_deleted = models.BooleanField(default=False, verbose_name="Supprimé")
    class Meta(SoftDeleteModel.Meta):
        verbose_name = "Acompte"
        verbose_name_plural = "Acomptes"
        unique_together = ['dossier', 'annee']
        ordering = ['-annee']

    def __str__(self):
        return f"Acomptes {self.annee} - {self.dossier.denomination}"

    @property
    def total_acomptes(self):
        """Calcule le total des acomptes versés"""
        return self.a1 + self.a2 + self.a3 + self.a4


class CMIR(SoftDeleteModel):
    """
    Modèle pour le suivi des CM (Cotisation Minimale) et IR (Impôt sur le Revenu)
    """
    dossier = models.ForeignKey(
        Dossier,
        on_delete=models.CASCADE,
        related_name='cm_ir',
        verbose_name="Dossier"
    )
    code = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        null=True,
    )
    annee = models.IntegerField(
        verbose_name="Année"
    )
    montant_ir = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="Montant IR"
    )
    montant_cm = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="Montant CM"
    )
    complement_ir = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Complément IR"
    )
    
    # Métadonnées
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta(SoftDeleteModel.Meta):
        verbose_name = "CM et IR"
        verbose_name_plural = "CM et IR"
        unique_together = ['dossier', 'annee']
        ordering = ['-annee']

    def __str__(self):
        return f"CM/IR {self.annee} - {self.dossier.denomination}"


class SuiviForfaitaire(SoftDeleteModel):
    """
    Modèle pour le suivi des déclarations et paiements forfaitaires (IR, 9421, acomptes)
   
    """
    # Identifiants
    dossier = models.ForeignKey(
        Dossier,
        on_delete=models.CASCADE,
        related_name='suivis_forfaitaires',
        verbose_name="Dossier"
    )
    annee = models.IntegerField(
        verbose_name="Année"
    )
    
    code = models.CharField(
        max_length=10,
        blank=True,
        verbose_name="Code Forfaitaire"
    )
    pp = models.CharField(
        max_length=10,
        blank=True,
        verbose_name="Référence PP"
    )
   
    paiement_annuel = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Montant Paiement Annuel"
    )

    ir = models.CharField(max_length=20, blank=True, verbose_name="Code IR")
    code_9421 = models.CharField(max_length=20, blank=True, verbose_name="Code 9421")

    
    # Paiements trimestriels
    acompte_1 = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="1er Acompte"
    )
    acompte_2 = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="2ème Acompte"
    )
    acompte_3 = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="3ème Acompte"
    )
    acompte_4 = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="4ème Acompte"
    )

    # Métadonnées
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta(SoftDeleteModel.Meta):
        verbose_name = "Suivi Forfaitaire"
        verbose_name_plural = "Suivis Forfaitaires"
        unique_together = ['dossier', 'annee']
        ordering = ['-annee']

    def __str__(self):
        return f"Suivi Forfaitaire {self.annee} - {self.dossier.denomination}"
    

class DepotBilan(SoftDeleteModel):
    """
    Modèle pour le suivi des dépôts de bilans
    """
    dossier = models.ForeignKey(
        Dossier,
        on_delete=models.CASCADE,
        related_name='depots_bilan',
        verbose_name="Dossier"
    )
    code = models.CharField(
        max_length=10,
        blank=True,
        verbose_name="Code Dépot Bilan"
    )
    annee_exercice = models.IntegerField(
        verbose_name="Année d'exercice"
    )
    date_depot = models.DateField(
        blank=True,
        null=True,
        verbose_name="Date de dépôt"
    )
    remarque = models.TextField(
        blank=True,
        null=True,
        verbose_name="Remarques"
    )
    
    # Statut
    STATUT_CHOICES = [
        ('EN_ATTENTE', 'En attente'),
        ('DEPOSE', 'Déposé'),
        ('RETARD', 'En retard'),
        ('EXEMPTE', 'Exempté'),
    ]
    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default='EN_ATTENTE',
        verbose_name="Statut"
    )
    
    # Métadonnées
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta(SoftDeleteModel.Meta):
        verbose_name = "Dépôt de bilan"
        verbose_name_plural = "Dépôts de bilans"
        unique_together = ['dossier', 'annee_exercice']
        ordering = ['-annee_exercice']

    def __str__(self):
        return f"Dépôt bilan {self.annee_exercice} - {self.dossier.denomination}"




