# ==================== Imports ====================
from django.test import TestCase
from decimal import Decimal
from dossiers.models import Dossier
from comptables.models import Comptable
from utilisateurs.models import Utilisateur
from .models import Honoraire, HonorairePV, ReglementHonoraire, ReglementHonorairePV
from datetime import date

# ==================== Classes ====================
class HonoraireModelTest(TestCase):
    def setUp(self):
        self.user = Utilisateur.objects.create_user(username='honoraire_user', password='password', role='comptable')
        self.comptable = Comptable.objects.create(user=self.user, nom='Doe', prenom='John', email='john@example.com')
        self.dossier = Dossier.objects.create(
            code='P',
            denomination='Client H',
            forme_juridique='SARL',
            secteur_activites='Audit',
            branche_activite='Conseil',
            adresse='123 Road',
            comptable_traitant=self.comptable
        )

    def test_honoraire_creation(self):
        honoraire = Honoraire.objects.create(
            dossier=self.dossier,
            montant_mensuel=Decimal('1000.00'),
            montant_trimestriel=Decimal('3000.00'),
            montant_annuel=Decimal('12000.00')
        )
        self.assertEqual(honoraire.montant_mensuel, Decimal('1000.00'))
        self.assertEqual(str(honoraire), f"Honoraires - {self.dossier.denomination}")

    def test_reglement_honoraire_impact(self):
        honoraire = Honoraire.objects.create(
            dossier=self.dossier,
            montant_mensuel=Decimal('1000.00')
        )
        reglement = ReglementHonoraire.objects.create(
            honoraire=honoraire,
            date_reglement=date.today(),
            montant=Decimal('600.00'),
            type_reglement='MENSUEL'
        )
        self.assertEqual(honoraire.total_reglements_mensuel, Decimal('600.00'))
        self.assertEqual(honoraire.reste_mensuel, Decimal('400.00'))

    def test_honoraire_pv_creation(self):
        pv = HonorairePV.objects.create(
            dossier=self.dossier,
            montant_total=Decimal('5000.00'),
            description="PV de test"
        )
        self.assertEqual(pv.montant_total, Decimal('5000.00'))
        self.assertEqual(pv.reste_pv, Decimal('5000.00'))

    def test_reglement_honoraire_pv(self):
        pv = HonorairePV.objects.create(dossier=self.dossier, montant_total=Decimal('5000.00'))
        reglement = ReglementHonorairePV.objects.create(
            honoraire_pv=pv,
            date_reglement=date.today(),
            montant=Decimal('2000.00'),
            type_reglement='CHEQUE'
        )
        self.assertEqual(pv.total_reglements_pv, Decimal('2000.00'))
        self.assertEqual(pv.reste_pv, Decimal('3000.00'))

    def test_soft_delete(self):
        honoraire = Honoraire.objects.create(dossier=self.dossier)
        honoraire.soft_delete()
        self.assertTrue(honoraire.is_deleted)
        self.assertFalse(Honoraire.objects.filter(pk=honoraire.pk).exists())
