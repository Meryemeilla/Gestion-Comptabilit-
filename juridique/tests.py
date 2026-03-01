# ==================== Imports ====================
from django.test import TestCase
from dossiers.models import Dossier
from comptables.models import Comptable
from utilisateurs.models import Utilisateur
from .models import JuridiqueCreation, DocumentJuridique, EvenementJuridique
from datetime import date

# ==================== Classes ====================
class JuridiqueModelTest(TestCase):
    def setUp(self):
        self.user = Utilisateur.objects.create_user(username='juridique_user', password='password', role='comptable')
        self.comptable = Comptable.objects.create(user=self.user, nom='Doe', prenom='John', email='john@example.com')
        self.dossier = Dossier.objects.create(
            code='P',
            denomination='Client J',
            forme_juridique='SARL',
            secteur_activites='Juridique',
            branche_activite='Conseil',
            adresse='456 Street',
            comptable_traitant=self.comptable
        )

    def test_juridique_creation_creation(self):
        juridique = JuridiqueCreation.objects.create(
            dossier=self.dossier,
            certificat_negatif=True,
            statuts=True
        )
        self.assertEqual(juridique.statut_global, 'EN_COURS')
        self.assertAlmostEqual(juridique.pourcentage_completion, (2/9) * 100)
        self.assertEqual(str(juridique), f"Création juridique - {self.dossier.denomination}")

    def test_document_juridique_creation(self):
        doc = DocumentJuridique.objects.create(
            dossier=self.dossier,
            nom_document='Statuts signés',
            type_document='PROCES_VERBAL',
            date_document=date.today()
        )
        self.assertEqual(doc.nom_document, 'Statuts signés')
        self.assertEqual(str(doc), f"Statuts signés ({self.dossier.denomination})")

    def test_evenement_juridique_creation(self):
        event = EvenementJuridique.objects.create(
            dossier=self.dossier,
            type_evenement='ASSEMBLEE_GENERALE',
            date_evenement=date.today(),
            statut='PLANIFIE'
        )
        self.assertEqual(event.statut, 'PLANIFIE')
        self.assertIn('ASSEMBLEE_GENERALE', str(event))
