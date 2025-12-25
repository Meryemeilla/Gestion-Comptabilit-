"""
Module applicatif.

Fichier: comptables/management/commands/update_comptable_stats.py
"""

# ==================== Imports ====================
from django.core.management.base import BaseCommand
from comptables.models import Comptable

# ==================== Classes ====================
class Command(BaseCommand):
    help = 'Met à jour les statistiques (nbre_pm, nbre_et) pour tous les comptables.'

    def handle(self, *args, **options):
        self.stdout.write('Mise à jour des statistiques des comptables...')
        comptables = Comptable.objects.all()
        for comptable in comptables:
            comptable.calculer_statistiques()
            self.stdout.write(f'Statistiques mises à jour pour {comptable.nom_complet}')
        self.stdout.write(self.style.SUCCESS('Toutes les statistiques des comptables ont été mises à jour avec succès.'))