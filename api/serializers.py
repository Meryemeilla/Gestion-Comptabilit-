from rest_framework import serializers
from comptables.models import Comptable
from dossiers.models import Dossier
from honoraires.models import Honoraire, ReglementHonoraire, HonorairePV, ReglementHonorairePV
from fiscal.models import SuiviTVA, Acompte, CMIR, DepotBilan, SuiviForfaitaire
from reclamations.models import Reclamation
from juridique.models import JuridiqueCreation, DocumentJuridique, EvenementJuridique


class ComptableSerializer(serializers.ModelSerializer):
    nom_complet = serializers.ReadOnlyField()
    
    class Meta:
        model = Comptable
        fields = '__all__'
        read_only_fields = ['nbre_pm', 'nbre_et', 'nbre_personn', 'nbre_bureau', 'date_creation', 'date_modification']


class ComptableListSerializer(serializers.ModelSerializer):
    nom_complet = serializers.ReadOnlyField()
    
    class Meta:
        model = Comptable
        fields = ['id', 'matricule', 'nom_complet', 'email', 'tel', 'nbre_pm', 'nbre_et', 'actif']


class DossierSerializer(serializers.ModelSerializer):
    comptable_traitant_nom = serializers.CharField(source='comptable_traitant.nom_complet', read_only=True)
    est_pm = serializers.ReadOnlyField()
    est_pp = serializers.ReadOnlyField()
    est_forfaitaire = serializers.ReadOnlyField()
    a_tva = serializers.ReadOnlyField()
    
    class Meta:
        model = Dossier
        fields = '__all__'
        read_only_fields = ['date_creation_dossier', 'date_modification']


class DossierListSerializer(serializers.ModelSerializer):
    comptable_traitant_nom = serializers.CharField(source='comptable_traitant.nom_complet', read_only=True)
    
    class Meta:
        model = Dossier
        fields = [
            'id', 'denomination', 'code', 'forme_juridique', 'declaration_tva',
            'comptable_traitant', 'comptable_traitant_nom', 'statut', 'actif'
        ]


class HonoraireSerializer(serializers.ModelSerializer):
    dossier_nom = serializers.CharField(source='dossier.denomination', read_only=True)
    reste_mensuel = serializers.ReadOnlyField()
    reste_trimestriel = serializers.ReadOnlyField()
    reste_annuel = serializers.ReadOnlyField()
    total_reglements_mensuel = serializers.ReadOnlyField()
    total_reglements_trimestriel = serializers.ReadOnlyField()
    total_reglements_annuel = serializers.ReadOnlyField()
    
    class Meta:
        model = Honoraire
        fields = '__all__'
        read_only_fields = ['date_creation', 'date_modification']


class ReglementHonoraireSerializer(serializers.ModelSerializer):
    honoraire_dossier = serializers.CharField(source='honoraire.dossier.denomination', read_only=True)
    
    class Meta:
        model = ReglementHonoraire
        fields = '__all__'
        read_only_fields = ['date_creation', 'date_modification']


class HonorairePVSerializer(serializers.ModelSerializer):
    total_reglements_pv = serializers.ReadOnlyField()
    reste_pv = serializers.ReadOnlyField()

    class Meta:
        model = HonorairePV
        fields = '__all__'


class ReglementHonorairePVSerializer(serializers.ModelSerializer):
    honoraire_pv_code = serializers.CharField(source='honoraire_pv.code', read_only=True)

    class Meta:
        model = ReglementHonorairePV
        fields = '__all__'



class SuiviTVASerializer(serializers.ModelSerializer):
    dossier_nom = serializers.CharField(source='dossier.denomination', read_only=True)
    pourcentage_mensuel_complete = serializers.ReadOnlyField()
    pourcentage_trimestriel_complete = serializers.ReadOnlyField()
    
    class Meta:
        model = SuiviTVA
        fields = '__all__'
        read_only_fields = ['date_creation', 'date_modification']


class AcompteSerializer(serializers.ModelSerializer):
    dossier_nom = serializers.CharField(source='dossier.denomination', read_only=True)
    total_acomptes = serializers.ReadOnlyField()
    
    class Meta:
        model = Acompte
        fields = '__all__'
        read_only_fields = ['date_creation', 'date_modification']


class CMIRSerializer(serializers.ModelSerializer):
    dossier_nom = serializers.CharField(source='dossier.denomination', read_only=True)
    
    class Meta:
        model = CMIR
        fields = '__all__'
        read_only_fields = ['date_creation', 'date_modification']


class DepotBilanSerializer(serializers.ModelSerializer):
    dossier_nom = serializers.CharField(source='dossier.denomination', read_only=True)
    
    class Meta:
        model = DepotBilan
        fields = '__all__'
        read_only_fields = ['date_creation', 'date_modification']


class SuiviForfaitaireSerializer(serializers.ModelSerializer):
    dossier_nom = serializers.CharField(source='dossier.denomination', read_only=True)
    pourcentage_acomptes_payes = serializers.ReadOnlyField()
    
    class Meta:
        model = SuiviForfaitaire
        fields = '__all__'
        read_only_fields = ['date_creation', 'date_modification']


class ReclamationSerializer(serializers.ModelSerializer):
    dossier_nom = serializers.CharField(source='dossier.denomination', read_only=True)
    
    class Meta:
        model = Reclamation
        fields = '__all__'
        read_only_fields = ['date_creation', 'date_modification']


class JuridiqueCreationSerializer(serializers.ModelSerializer):
    dossier_nom = serializers.CharField(source='dossier.denomination', read_only=True)
    pourcentage_completion = serializers.ReadOnlyField()
    formalites_manquantes = serializers.ReadOnlyField()
    
    class Meta:
        model = JuridiqueCreation
        fields = '__all__'
        read_only_fields = ['date_creation', 'date_modification']


class DocumentJuridiqueSerializer(serializers.ModelSerializer):
    dossier_nom = serializers.CharField(source='dossier.denomination', read_only=True)
    
    class Meta:
        model = DocumentJuridique
        fields = '__all__'
        read_only_fields = ['date_creation', 'date_modification']


class EvenementJuridiqueSerializer(serializers.ModelSerializer):
    dossier_nom = serializers.CharField(source='dossier.denomination', read_only=True)
    
    class Meta:
        model = EvenementJuridique
        fields = '__all__'
        read_only_fields = ['date_creation', 'date_modification']


# Serializers pour les statistiques et rapports
class StatistiquesComptableSerializer(serializers.Serializer):
    comptable = ComptableListSerializer()
    total_dossiers = serializers.IntegerField()
    dossiers_pm = serializers.IntegerField()
    dossiers_pp = serializers.IntegerField()
    dossiers_forfaitaires = serializers.IntegerField()
    dossiers_avec_tva = serializers.IntegerField()
    dossiers_sans_tva = serializers.IntegerField()


class StatistiquesCabinetSerializer(serializers.Serializer):
    total_comptables = serializers.IntegerField()
    total_dossiers = serializers.IntegerField()
    total_dossiers_actifs = serializers.IntegerField()
    total_pm = serializers.IntegerField()
    total_pp = serializers.IntegerField()
    total_forfaitaires = serializers.IntegerField()
    total_avec_tva_mensuelle = serializers.IntegerField()
    total_avec_tva_trimestrielle = serializers.IntegerField()
    total_exoneres_tva = serializers.IntegerField()
    repartition_par_secteur = serializers.DictField()
    repartition_par_forme_juridique = serializers.DictField()

