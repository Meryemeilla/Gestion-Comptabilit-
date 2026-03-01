# ==================== Imports ====================
from django.test import TestCase
from decimal import Decimal
from dossiers.models import Dossier
from comptables.models import Comptable
from utilisateurs.models import Utilisateur
from .models import SuiviTVA, Acompte, CMIR, SuiviForfaitaire, DepotBilan

# ==================== Classes ====================
class FiscalModelTest(TestCase):
    def setUp(self):
        self.user = Utilisateur.objects.create_user(username='fiscal_user', password='password', role='comptable')
        self.comptable = Comptable.objects.create(user=self.user, nom='Doe', prenom='John', email='john@example.com')
        self.dossier = Dossier.objects.create(
            code='P',
            denomination='Test Enterprise',
            forme_juridique='SARL',
            secteur_activites='IT',
            branche_activite='Dev',
            adresse='123 Street',
            comptable_traitant=self.comptable
        )

    def test_suivitva_creation(self):
        suivi = SuiviTVA.objects.create(dossier=self.dossier, annee=2024, jan=True, fev=True)
        self.assertEqual(suivi.annee, 2024)
        self.assertEqual(suivi.pourcentage_mensuel_complete, (2/12) * 100)
        self.assertTrue(suivi.code.startswith(tuple('ABCDEFGHIJKLMNOPQRSTUVWXYZ')))

    def test_acompte_creation(self):
        acompte = Acompte.objects.create(
            dossier=self.dossier, 
            annee=2024, 
            a1=Decimal('1000.00'), 
            a2=Decimal('1000.00')
        )
        self.assertEqual(acompte.total_acomptes, Decimal('2000.00'))

    def test_cmir_creation(self):
        cmir = CMIR.objects.create(
            dossier=self.dossier, 
            annee=2024, 
            montant_ir=Decimal('5000.00'), 
            montant_cm=Decimal('1500.00')
        )
        self.assertEqual(cmir.montant_ir, Decimal('5000.00'))
        self.assertEqual(str(cmir), f"CM/IR 2024 - {self.dossier.denomination}")

    def test_suivi_forfaitaire_creation(self):
        forfaitaire = SuiviForfaitaire.objects.create(dossier=self.dossier, annee=2024, acompte_1=Decimal('500.00'))
        self.assertEqual(forfaitaire.acompte_1, Decimal('500.00'))

    def test_depot_bilan_creation(self):
        depot = DepotBilan.objects.create(dossier=self.dossier, annee_exercice=2023, statut='DEPOSE')
        self.assertEqual(depot.statut, 'DEPOSE')
        self.assertEqual(str(depot), f"Dépôt bilan 2023 - {self.dossier.denomination}")

    def test_soft_delete(self):
        suivi = SuiviTVA.objects.create(dossier=self.dossier, annee=2024)
        suivi.soft_delete()
        self.assertTrue(suivi.is_deleted)
        self.assertFalse(SuiviTVA.objects.filter(pk=suivi.pk).exists())
        self.assertTrue(SuiviTVA.all_objects.filter(pk=suivi.pk).exists())
