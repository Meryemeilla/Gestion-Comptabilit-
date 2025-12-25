"""
Services métier réutilisables et testables.

Fichier: dossiers/services.py
"""

# ==================== Imports ====================
from django.db.models import Q
from django.db.models import Count
from dossiers.models import Dossier


# ==================== Fonctions ====================
def get_stats_by_year_month():
    """Retourne les statistiques agrégées par année et mois avec noms de mois."""
    return Dossier.objects.stats_by_year_month()


def get_total_cards():
    """Calcule les totaux affichés dans les cartes du tableau de stats."""
    return {
        'total_dossiers': Dossier.objects.active().count(),
        'total_pp': Dossier.objects.filter(forme_juridique__in=['EI', 'EIRL', 'AUTO', 'EURL']).count(),
        'total_pm': Dossier.objects.exclude(forme_juridique__in=['EI', 'EIRL', 'AUTO', 'EURL', 'AUTRE']).count(),
        'tva_mensuelle': Dossier.objects.filter(declaration_tva='MENSUELLE').count(),
        'tva_trimestrielle': Dossier.objects.filter(declaration_tva='TRIMESTRIELLE').count(),
        'tva_exoneree': Dossier.objects.filter(declaration_tva='EXONEREE').count(),
        'total_radie': Dossier.objects.filter(statut='RADIE', is_deleted=False).count(),
        'total_livre': Dossier.objects.filter(statut='LIVRE', is_deleted=False).count(),
        'total_delaisse': Dossier.objects.filter(statut='DELAISSE', is_deleted=False).count(),
    }


def get_sector_counts():
    """Statistiques des dossiers actifs par secteur d'activités."""
    return list(Dossier.objects.by_secteur_counts())


def get_branche_counts():
    """Statistiques des dossiers actifs par branche d'activité."""
    return list(Dossier.objects.by_branche_counts())