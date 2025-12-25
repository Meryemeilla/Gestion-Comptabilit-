"""
Modèles Django et logique d’accès aux données.

Fichier: juridique/models.py
"""

# ==================== Imports ====================
from django.db import models
from django.db import models
from dossiers.models import Dossier


# ==================== Classes ====================
class JuridiqueCreation(models.Model):
    """
    Modèle pour la gestion des informations juridiques liées aux créations d'entreprises
    """
    dossier = models.OneToOneField(
        Dossier,
        on_delete=models.CASCADE,
        related_name='juridique_creation',
        verbose_name="Dossier"
    )
    code = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        null=True,
        
    )
    
    # Informations de base
    ordre = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Ordre"
    )
    forme = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Forme"
    )
    
    # Documents et formalités
    certificat_negatif = models.BooleanField(
        default=False,
        verbose_name="Certificat négatif"
    )
    date_certificat_negatif = models.DateField(
        blank=True,
        null=True,
        verbose_name="Date certificat négatif"
    )
    
    statuts = models.BooleanField(
        default=False,
        verbose_name="Statuts"
    )
    date_statuts = models.DateField(
        blank=True,
        null=True,
        verbose_name="Date statuts"
    )
    
    contrat_bail = models.BooleanField(
        default=False,
        verbose_name="Contrat de bail"
    )
    date_contrat_bail = models.DateField(
        blank=True,
        null=True,
        verbose_name="Date contrat de bail"
    )
    
    # Formalités administratives
    tp = models.BooleanField(
        default=False,
        verbose_name="TP (Taxe Professionnelle)"
    )
    date_tp = models.DateField(
        blank=True,
        null=True,
        verbose_name="Date TP"
    )
    
    rc = models.BooleanField(
        default=False,
        verbose_name="RC (Registre de Commerce)"
    )
    date_rc = models.DateField(
        blank=True,
        null=True,
        verbose_name="Date RC"
    )
    numero_rc = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Numéro RC"
    )
    
    cnss = models.BooleanField(
        default=False,
        verbose_name="CNSS"
    )
    date_cnss = models.DateField(
        blank=True,
        null=True,
        verbose_name="Date CNSS"
    )
    numero_cnss = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Numéro CNSS"
    )
    
    al = models.BooleanField(
        default=False,
        verbose_name="AL (Autorisation de Location)"
    )
    date_al = models.DateField(
        blank=True,
        null=True,
        verbose_name="Date AL"
    )
    
    bo = models.BooleanField(
        default=False,
        verbose_name="BO (Bulletin Officiel)"
    )
    date_bo = models.DateField(
        blank=True,
        null=True,
        verbose_name="Date BO"
    )
    
    rq = models.BooleanField(
        default=False,
        verbose_name="RQ (Registre de Qualité)"
    )
    date_rq = models.DateField(
        blank=True,
        null=True,
        verbose_name="Date RQ"
    )
    
    # Statut global
    STATUT_CHOICES = [
        ('EN_COURS', 'En cours'),
        ('COMPLETE', 'Complète'),
        ('EN_ATTENTE', 'En attente'),
        ('BLOQUEE', 'Bloquée'),
    ]
    statut_global = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default='EN_COURS',
        verbose_name="Statut global"
    )
    
    # Remarques
    remarques = models.TextField(
        blank=True,
        null=True,
        verbose_name="Remarques"
    )
    
    # Métadonnées
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Juridique - Création"
        verbose_name_plural = "Juridiques - Créations"

    def __str__(self):
        return f"Création juridique - {self.dossier.denomination}"

    @property
    def pourcentage_completion(self):
        """Calcule le pourcentage de completion des formalités"""
        formalites = [
            self.certificat_negatif,
            self.statuts,
            self.contrat_bail,
            self.tp,
            self.rc,
            self.cnss,
            self.al,
            self.bo,
            self.rq
        ]
        return (sum(formalites) / len(formalites)) * 100

    @property
    def formalites_manquantes(self):
        """Retourne la liste des formalités manquantes"""
        manquantes = []
        if not self.certificat_negatif:
            manquantes.append("Certificat négatif")
        if not self.statuts:
            manquantes.append("Statuts")
        if not self.contrat_bail:
            manquantes.append("Contrat de bail")
        if not self.tp:
            manquantes.append("TP")
        if not self.rc:
            manquantes.append("RC")
        if not self.cnss:
            manquantes.append("CNSS")
        if not self.al:
            manquantes.append("AL")


class DocumentJuridique(models.Model):
    TYPE_DOCUMENT_CHOICES = [
        ('CONTRAT', 'Contrat'),
        ('PROCES_VERBAL', 'Procès-verbal'),
        ('ATTESTATION', 'Attestation'),
        ('AUTRE', 'Autre'),
    ]
    STATUT_CHOICES = [
        ('BROUILLON', 'Brouillon'),
        ('VALIDE', 'Validé'),
        ('ARCHIVE', 'Archivé'),
        ('ANNULE', 'Annulé'),
    ]

    dossier = models.ForeignKey(
        Dossier,
        on_delete=models.CASCADE,
        related_name='documents_juridiques',
        verbose_name="Dossier"
    )
    code = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        null=True,
        
    )
    nom_document = models.CharField(
        max_length=255,
        verbose_name="Nom du document"
    )
    type_document = models.CharField(
        max_length=50,
        choices=TYPE_DOCUMENT_CHOICES,
        default='AUTRE',
        verbose_name="Type de document"
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Description"
    )
    fichier = models.FileField(
        upload_to='documents_juridiques/',
        blank=True,
        null=True,
        verbose_name="Fichier"
    )
    date_document = models.DateField(
        blank=True,
        null=True,
        verbose_name="Date du document"
    )
    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default='BROUILLON',
        verbose_name="Statut"
    )
    numero_document = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Numéro de document"
    )
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Document Juridique"
        verbose_name_plural = "Documents Juridiques"
        ordering = ['-date_document']

    def __str__(self):
        return f"{self.nom_document} ({self.dossier.denomination})"


class EvenementJuridique(models.Model):
    TYPE_EVENEMENT_CHOICES = [
        ('ASSEMBLEE_GENERALE', 'Assemblée Générale'),
        ('CONSEIL_ADMINISTRATION', 'Conseil d\'Administration'),
        ('DEPOT_COMPTES', 'Dépôt des comptes'),
        ('MODIFICATION_STATUTS', 'Modification des statuts'),
        ('AUTRE', 'Autre'),
    ]
    STATUT_CHOICES = [
        ('PLANIFIE', 'Planifié'),
        ('REALISE', 'Réalisé'),
        ('ANNULE', 'Annulé'),
        ('REPORTE', 'Reporté'),
    ]

    dossier = models.ForeignKey(
        Dossier,
        on_delete=models.CASCADE,
        related_name='evenements_juridiques',
        verbose_name="Dossier"
    )
    code = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        null=True,
        
    )
    type_evenement = models.CharField(
        max_length=50,
        choices=TYPE_EVENEMENT_CHOICES,
        default='AUTRE',
        verbose_name="Type d'événement"
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Description"
    )
    date_evenement = models.DateField(
        verbose_name="Date de l'événement"
    )
    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default='PLANIFIE',
        verbose_name="Statut"
    )
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name="Notes"
    )
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Événement Juridique"
        verbose_name_plural = "Événements Juridiques"
        ordering = ['-date_evenement']

    def __str__(self):
        return f"{self.type_evenement} pour {self.dossier.denomination} le {self.date_evenement}"

