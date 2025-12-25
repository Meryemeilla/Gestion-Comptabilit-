"""
Managers ORM personnalisés pour les QuerySets.

Fichier: dossiers/managers.py
"""

# ==================== Imports ====================
from django.db import models
from django.db.models import Count, Q
from django.db.models.functions import ExtractYear, ExtractMonth
from cabinet.soft_delete_models import SoftDeleteManager


# ==================== Classes ====================
class DossierQuerySet(models.QuerySet):
    def active(self):
        return self.filter(actif=True)

    def pm(self):
        return self.active().filter(forme_juridique__in=['SARL', 'SA', 'SNC', 'SCS', 'SCA', 'EURL', 'SASU', 'SAS'])

    def pp(self):
        return self.active().filter(forme_juridique__in=['EI', 'EIRL', 'AUTO', 'EURL'])

    def with_tva(self):
        return self.active().filter(declaration_tva__in=['MENSUELLE', 'TRIMESTRIELLE'])

    def by_secteur_counts(self):
        return (
            self.active()
            .values('secteur_activites')
            .annotate(total=Count('id'))
            .order_by('secteur_activites')
        )

    def by_branche_counts(self):
        return (
            self.active()
            .values('branche_activite')
            .annotate(total=Count('id'))
            .order_by('branche_activite')
        )

    def stats_by_year_month(self):
        qs = (
            self.annotate(year=ExtractYear('date_creation'), month=ExtractMonth('date_creation'))
            .values('year', 'month')
            .annotate(
                dossiers_pp=Count('id', filter=Q(forme_juridique__in=['EI', 'EIRL', 'AUTO'], actif=True)),
                dossiers_pm=Count('id', filter=Q(forme_juridique__in=['SARL', 'SA', 'SNC', 'SCS', 'SCA', 'EURL', 'SASU', 'SAS'], actif=True)),
                dossiers_avec_tva=Count('id', filter=Q(declaration_tva__in=['MENSUELLE', 'TRIMESTRIELLE'], actif=True)),
                total=Count('id', filter=Q(actif=True)),
            )
            .order_by('year', 'month')
        )
        month_names = {
            1: 'Janvier', 2: 'Février', 3: 'Mars', 4: 'Avril', 5: 'Mai', 6: 'Juin',
            7: 'Juillet', 8: 'Août', 9: 'Septembre', 10: 'Octobre', 11: 'Novembre', 12: 'Décembre'
        }
        stats = list(qs)
        for stat in stats:
            stat['month'] = month_names.get(stat['month'], stat['month'])
        return stats


# Inherit SoftDeleteManager to preserve soft-delete behaviour while exposing our custom queryset
DossierManager = SoftDeleteManager.from_queryset(DossierQuerySet)