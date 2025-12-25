"""
Modèles Django et logique d’accès aux données.

Fichier: dossiers/models.py
"""

# ==================== Imports ====================
from django.db import models
from django.core.validators import RegexValidator
from comptables.models import Comptable
from utilisateurs.models import Client
from django.conf import settings
import re
from PyPDF2 import PdfReader  # Assure-toi que PyPDF2 est installé
from cabinet.soft_delete_models import SoftDeleteModel, SoftDeleteManager
from .managers import DossierManager

# ==================== Classes ====================
class Dossier(SoftDeleteModel):
    """
    Modèle représentant un dossier d'entreprise
    """
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="dossiers_client", null=True, blank=True, verbose_name="Client")
    

    cree_par = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        related_name='dossiers_crees',
        null=True, blank=True,
        on_delete=models.SET_NULL
    )
    # Choix pour les codes de dossier
    CODE_CHOICES = [
        ('P', 'P - Personne physique'),
        ('S', 'S - Société'),
        ('F', 'F - Forfaitaire'),
        ('R', 'R - Radié'),
        ('L', 'L - Livré'),
        ('D', 'D - Délaissé')
    ]
    
    # Choix pour les formes juridiques
    FORME_JURIDIQUE_CHOICES = [
        ('SARL', 'SARL - Société à Responsabilité Limitée'),
        ('SA', 'SA - Société Anonyme'),
        ('SNC', 'SNC - Société en Nom Collectif'),
        ('SCS', 'SCS - Société en Commandite Simple'),
        ('SCA', 'SCA - Société en Commandite par Actions'),
        ('EURL', 'EURL - Entreprise Unipersonnelle à Responsabilité Limitée'),
        ('SASU', 'SASU - Société par Actions Simplifiée Unipersonnelle'),
        ('SAS', 'SAS - Société par Actions Simplifiée'),
        ('EI', 'EI - Entreprise Individuelle'),
        ('PP', 'PP - Personne Physique'),
        ('EIRL', 'EIRL - Entreprise Individuelle à Responsabilité Limitée'),
        ('AUTO', 'Auto-entrepreneur'),
        ('AUTRE', 'Autre'),
    ]
    
    # Choix pour la déclaration TVA
    DECLARATION_TVA_CHOICES = [
        ('MENSUELLE', 'TVA Mensuelle'),
        ('TRIMESTRIELLE', 'TVA Trimestrielle'),
        ('EXONEREE', 'Exonérée de la TVA'),
    ]
    
    # Informations de base
    code = models.CharField(
        max_length=10,
        choices=CODE_CHOICES,
        verbose_name="Code du dossier"
    )
    denomination = models.CharField(
        max_length=200,
        verbose_name="Dénomination de l'entreprise"
    )
    abreviation = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Abréviation"
    )
    forme_juridique = models.CharField(
        max_length=20,
        choices=FORME_JURIDIQUE_CHOICES,
        verbose_name="Forme juridique"
    )
    date_creation = models.DateField(
        verbose_name="Date de création de l'entreprise",
        null=True,
        blank=True
    )
    secteur_activites = models.CharField(
        max_length=200,
        verbose_name="Secteur d'activités"
    )
    branche_activite = models.CharField(
        max_length=200,
        verbose_name="Branche d'activité"
    )
    
    # Coordonnées
    adresse = models.TextField(
        verbose_name="Adresse"
    )
    email = models.EmailField(
        blank=True,
        null=True,
        verbose_name="Email de l'entreprise"
    )
    fixe = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="Téléphone fixe",
        validators=[RegexValidator(
            regex=r'^[\+]?[0-9\s\-\(\)]{10,20}$',
            message='Format de téléphone invalide'
        )]
    )
    gsm = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="Téléphone mobile",
        validators=[RegexValidator(
            regex=r'^[\+]?[0-9\s\-\(\)]{10,20}$',
            message='Format de téléphone invalide'
        )]
    )
    
    # Personnes de contact
    gerant = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="Gérant"
    )
    personne_a_contacter = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="Personne à contacter"
    )
    
    # Identifiants officiels
    if_identifiant = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="Identifiant Fiscal (IF)"
    )
    ice = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="Identifiant Commun de l'Entreprise (ICE)"
    )
    tp = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="Taxe Professionnelle (TP)"
    )
    rc = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="Registre de Commerce (RC)"
    )
    cnss = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="Numéro CNSS de l'entreprise"
    )
    
    # TVA
    declaration_tva = models.CharField(
        max_length=20,
        choices=DECLARATION_TVA_CHOICES,
        default='EXONEREE',
        verbose_name="Déclaration à la TVA"
    )
    annee_extraite_pdf = models.IntegerField(null=True, blank=True)
    dernier_rappel_tva = models.DateField(null=True, blank=True, verbose_name="Date du dernier rappel TVA")
    # dossier/models.py


    def extraire_annee_du_pdf(fichier_pdf):
        try:
            reader = PdfReader(fichier_pdf)
            texte = ""
            for page in reader.pages:
                texte += page.extract_text()
            match = re.search(r"(20\d{2})", texte)
            if match:
                return int(match.group(1))
        except Exception as e:
            print("Erreur extraction PDF :", e)
        return None

    
    # Relations
    comptable_traitant = models.ForeignKey(
        Comptable,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='dossiers',
        verbose_name="Comptable traitant"
    )
    
    # Métadonnées
    date_creation_dossier = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    actif = models.BooleanField(default=True, verbose_name="Actif")
    # is_deleted = models.BooleanField(default=False)
    
    # Statut du dossier
    STATUT_CHOICES = [
        ('EXISTANT', 'Existant'),
        ('RADIE', 'Radié'),
        ('LIVRE', 'Livré'),
        ('DELAISSE', 'Délaissé'),
    ]
    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default='EXISTANT',
        verbose_name="Statut du dossier"
    )
   

    # Statut fiscal
    STATUT_FISCAL_CHOICES = [
        ("A_JOUR", "À jour"),
        ("EN_RETARD", "En retard"),
        ("NON_COMMUNIQUE", "Non communiqué"),
    ]
    statut_fiscal = models.CharField(
        max_length=20,
        choices=STATUT_FISCAL_CHOICES,
        default="NON_COMMUNIQUE",
        blank=True,
        null=True,
        verbose_name="Statut fiscal"
    )

    objects = DossierManager()
    all_objects = models.Manager()

    class Meta(SoftDeleteModel.Meta):
        verbose_name = "Dossier"
        verbose_name_plural = "Dossiers"
        ordering = ['denomination']
        unique_together = ['denomination', 'comptable_traitant']

    def __str__(self):
            client_name = self.client.nom_complet if self.client else "Sans client"
            return f"{client_name} - {self.denomination}"


    @property
    def est_pm(self):
        """
        Vérifie si c'est un dossier PM (Personne Morale)
        """
        return self.forme_juridique in ['SARL', 'SA', 'SNC', 'SCS', 'SCA', 'SASU', 'SAS']

    @property
    def est_pp(self):
        """
        Vérifie si c'est un dossier PP (Personne Physique)
        """
        return self.forme_juridique in ['EI', 'EIRL', 'AUTO','EURL']

    @property
    def est_forfaitaire(self):
        """
        Vérifie si c'est un dossier forfaitaire
        """
        return self.code in ['F', 'FS']

    def type_structure(self):
        if self.forme_juridique in ['EI', 'EIRL', 'AUTO','EURL']:
            return "Personne Physique"
        return "Personne Morale"

    @property
    def a_tva(self):
        """
        Vérifie si l'entreprise est assujettie à la TVA
        """
        return self.declaration_tva in ['MENSUELLE', 'TRIMESTRIELLE']

    def delete(self, *args, **kwargs):
        self.is_deleted = True
        self.save()

    def save(self, *args, **kwargs):
        # Synchroniser automatiquement le statut en fonction du code
        if self.code == 'D':
            self.statut = 'DELAISSE'
            self.actif = False
            self.is_deleted = True
        elif self.code == 'L':
            self.statut = 'LIVRE'
            self.actif = False
            self.is_deleted = True
        elif self.code == 'R':
            self.statut = 'RADIE'
            self.actif = False
            self.is_deleted = True
        else:
            self.statut = 'EXISTANT'
            self.actif = True
            self.is_deleted = False

        super().save(*args, **kwargs)

        if self.comptable_traitant:
            self.comptable_traitant.calculer_statistiques()

        if self.client and not self.client.nom_entreprise:
            self.client.nom_entreprise = self.denomination
            self.client.save()
    def statut_css_class(self):
        return {
            'EXISTANT': 'statut-existant',
            'RADIE': 'statut-radie',
            'DELAISSE': 'statut-delaisse',
            'LIVRE': 'statut-livre',
        }.get(self.statut, '')
    
    def get_absolute_url(self):
        return reverse('cabinet:dossier_detail', kwargs={'pk': self.pk})

    @property
    def nom_complet_createur(self):
        """
        Retourne le nom complet de la personne qui a créé le dossier.
        Si c'est un comptable lié à l'utilisateur, retourne son nom et prénom.
        Sinon retourne le nom d'utilisateur ou '-' si absent.
        """
        user = self.cree_par
        if not user:
            return '-'
        
        # Si l'utilisateur a un profil comptable lié, on retourne son nom complet
        if hasattr(user, 'comptable_profile'):
            comptable = user.comptable_profile
            return f"{comptable.nom} {comptable.prenom}"
        
        # Sinon on essaie de retourner un nom complet s'il existe, ou juste username
        full_name = getattr(user, 'full_name', None) or f"{getattr(user, 'first_name', '')} {getattr(user, 'last_name', '')}".strip()
        if full_name:
            return full_name
        return user.username or '-'




