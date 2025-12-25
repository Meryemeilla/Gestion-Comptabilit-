"""
Module applicatif.

Fichier: honoraires/management/commands/update_alertes.py
"""

# ==================== Imports ====================
from django.core.management.base import BaseCommand
from honoraires.models import Honoraire, ReglementHonoraire

# ==================== Classes ====================
class Command(BaseCommand):
    help = "Met à jour les statuts des honoraires et règlements selon les échéances."

    def handle(self, *args, **options):
        honoraires = Honoraire.objects.all()
        for hon in honoraires:
            hon.update_statut_reglement()
        reglements = ReglementHonoraire.objects.all()
        for reg in reglements:
            reg.update_statut_reglement()
        self.stdout.write(self.style.SUCCESS("Statuts des honoraires et règlements mis à jour."))