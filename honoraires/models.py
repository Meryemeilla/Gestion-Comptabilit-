"""
Modèles Django et logique d’accès aux données.

Fichier: honoraires/models.py
"""

# ==================== Imports ====================
from django.db import models

from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from dossiers.models import Dossier
from django.db.models import Sum
from cabinet.soft_delete_models import SoftDeleteModel, SoftDeleteManager


# ==================== Classes ====================
class HonoraireManager(SoftDeleteManager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


class Honoraire(SoftDeleteModel):
    objects = HonoraireManager()
    all_objects = models.Manager()
    """
    Modèle représentant les honoraires d'un dossier
    """
    dossier = models.OneToOneField(
        Dossier,
        on_delete=models.CASCADE,
        null= True,
        related_name='honoraire',
        verbose_name="Dossier"
    )
    code = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        null=True,
        
    )
    montant_mensuel = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="Montant mensuel"
    )
    montant_trimestriel = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="Montant trimestriel"
    )
    montant_annuel = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="Montant annuel"
    )
    
    # Champs pour alertes
    statut_reglement = models.CharField(
        max_length=50,
        choices=[('EN_ATTENTE', 'En attente'), ('EN_RETARD', 'En retard'), ('PAYE', 'Payé')],
        default='EN_ATTENTE',
        verbose_name="Statut du règlement"
    )
    date_echeance = models.DateField(
        null=True,
        blank=True,
        verbose_name="Date d'échéance"
    )
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    # Métadonnées
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta(SoftDeleteModel.Meta):
        verbose_name = "Honoraire"
        verbose_name_plural = "Honoraires"

    def __str__(self):
        if self.dossier and hasattr(self.dossier, 'denomination'):
            return f"Honoraires - {self.dossier.denomination}"
        return "Honoraires - Sans dossier"


    @property
    def total_reglements_mensuel(self):
        """Calcule le total des règlements mensuels"""
        return sum(r.montant for r in self.reglements.filter(type_reglement='MENSUEL'))

    @property
    def total_reglements_trimestriel(self):
        """Calcule le total des règlements trimestriels"""
        return sum(r.montant for r in self.reglements.filter(type_reglement='TRIMESTRIEL'))

    @property
    def total_reglements_annuel(self):
        """Calcule le total des règlements annuels"""
        return sum(r.montant for r in self.reglements.filter(type_reglement='ANNUEL'))

    @property
    def reste_mensuel(self):
        """Calcule le reste à payer mensuel"""
        return self.montant_mensuel - self.total_reglements_mensuel

    @property
    def reste_trimestriel(self):
        """Calcule le reste à payer trimestriel"""
        return self.montant_trimestriel - self.total_reglements_trimestriel

    @property
    def reste_annuel(self):
        """Calcule le reste à payer annuel"""
        return self.montant_annuel - self.total_reglements_annuel

    def update_statut_reglement(self):
        """
        Met à jour le statut du règlement selon la date d'échéance et le reste à payer.
        """
        from django.utils import timezone
        today = timezone.now().date()
        if self.date_echeance:
            if self.reste_mensuel > 0 or self.reste_trimestriel > 0 or self.reste_annuel > 0:
                if self.date_echeance < today:
                    self.statut_reglement = 'EN_RETARD'
                else:
                    self.statut_reglement = 'EN_ATTENTE'
            else:
                self.statut_reglement = 'PAYE'
            self.save(update_fields=['statut_reglement'])
class HonorairePV(models.Model):
    dossier = models.ForeignKey(Dossier, on_delete=models.CASCADE, related_name='honoraire_pvs',
        verbose_name="Dossier", null=True
    )
    code = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        null=True,
        
    )
    date_creation = models.DateField(auto_now_add=True)
    montant_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    description = models.TextField(blank=True, null=True)

    
    def __str__(self):
        if self.dossier and hasattr(self.dossier, 'denomination'):
            return f"Honoraire PV #{self.id} - {self.dossier.denomination}"
        return f"Honoraire PV #{self.id} - Sans dossier"


    @property
    def total_reglements_pv(self):
        return self.reglement_pv.aggregate(Sum('montant'))['montant__sum'] or 0

    @property
    def reste_pv(self):
        return self.montant_total - self.total_reglements_pv

    class Meta:
        verbose_name = "Honoraire PV"
        verbose_name_plural = "Honoraires PV"

class ReglementHonoraire(models.Model):
    """
    Modèle représentant un règlement d'honoraire
    """
    TYPE_REGLEMENT_CHOICES = [
        # Types pour Honoraire classique
        ('MENSUEL', 'Mensuel'),
        ('TRIMESTRIELLE', 'Trimestriel'),
        ('ANNUEL', 'Annuel'),

    ]

    honoraire = models.ForeignKey(
        Honoraire,
        on_delete=models.CASCADE,
        related_name='reglements',
        verbose_name="Honoraire",
        null=True, blank=True
    )
    honoraire_pv = models.ForeignKey(
        HonorairePV,
         on_delete=models.CASCADE, 
         blank=True, null=True, related_name='reglement_pv')
    date_reglement = models.DateField(
        verbose_name="Date du règlement"
    )
    montant = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Montant réglé"
    )
    type_reglement = models.CharField(
            max_length=50,
        choices=TYPE_REGLEMENT_CHOICES,
        verbose_name="Type de règlement",
        blank=True, null=True
    )
    # Champs pour alertes
    statut_reglement = models.CharField(
        max_length=20,
        choices=[('EN_ATTENTE', 'En attente'), ('EN_RETARD', 'En retard'), ('PAYE', 'Payé')],
        default='EN_ATTENTE',
        verbose_name="Statut du règlement"
    )
    date_echeance = models.DateField(
        null=True,
        blank=True,
        verbose_name="Date d'échéance"
    )
    
    # Informations complémentaires
    MODE_PAIEMENT_CHOICES = [
        ('ESPECES', 'Espèces'),
        ('CHEQUE', 'Chèque'),
        ('VIREMENT', 'Virement'),
        ('CARTE', 'Carte bancaire'),
        ('AUTRE', 'Autre'),
    ]
    mode_paiement = models.CharField(
        max_length=20,
        choices=MODE_PAIEMENT_CHOICES,
        default='CHEQUE',
        verbose_name="Mode de paiement"
    )
    numero_piece = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Numéro de pièce (chèque, virement, etc.)"
    )
    remarques = models.TextField(
        blank=True,
        null=True,
        verbose_name="Remarques"
    )
   
    def update_statut_reglement(self):
        """
        Met à jour le statut du règlement selon la date d'échéance et la date de règlement.
        """
        from django.utils import timezone
        today = timezone.now().date()
        if self.date_echeance:
            if not self.date_reglement or self.date_reglement > self.date_echeance:
                if self.date_echeance < today:
                    self.statut_reglement = 'EN_RETARD'
                else:
                    self.statut_reglement = 'EN_ATTENTE'
            else:
                self.statut_reglement = 'PAYE'
            self.save(update_fields=['statut_reglement'])
    
    # Métadonnées
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Règlement d'honoraire"





class ReglementHonorairePV(models.Model):
    honoraire_pv = models.ForeignKey(HonorairePV, on_delete=models.CASCADE, related_name='reglements_honoraire_pv')
    date_reglement = models.DateField()
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    type_reglement = models.CharField(
        max_length=50,
        choices=[
            ('ESPECES', 'Espèces'),
            ('CHEQUE', 'Chèque'),
            ('VIREMENT', 'Virement'),
            ('CARTE', 'Carte bancaire'),
            ('AUTRE', 'Autre'),
            ('PRELEVEMENT', 'Prélèvement'),
            ('VIREMENT_BANCAIRE', 'Virement Bancaire'),
            ('CARTE_CREDIT', 'Carte de Crédit'),
            ('AUTRE_MOYEN', 'Autre Moyen'),
        ],
        verbose_name="Type de règlement"
    )
    reference = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"Règlement PV de {self.montant} pour Honoraire PV {self.honoraire_pv.code}"

    class Meta:
        verbose_name = "Règlement Honoraire PV"
        verbose_name_plural = "Règlements Honoraires PV"
        ordering = ['-date_reglement']

    def __str__(self):
        return f"Règlement {self.montant} pour {self.honoraire_pv.code}"


