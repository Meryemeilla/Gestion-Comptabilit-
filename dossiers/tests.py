"""
Module applicatif.

Fichier: dossiers/tests.py
"""

# ==================== Imports ====================
from django.test import TestCase

# Create your tests here.


from django.test import TestCase
from .models import Dossier
from comptables.models import Comptable
from utilisateurs.models import Client
from django.contrib.auth import get_user_model

User = get_user_model()

# ==================== Classes ====================
class DossierModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.comptable = Comptable.objects.create(user=self.user, nom='Doe', prenom='John', email='john.doe@example.com')
        self.client = Client.objects.create(user=self.user, nom_entreprise='Client Test', email='client@example.com', contact_personne='Test Contact', telephone='1234567890')

    def test_dossier_creation(self):
        dossier = Dossier.objects.create(
            code='P',
            denomination='Entreprise Test',
            forme_juridique='SARL',
            secteur_activites='Informatique',
            branche_activite='Développement',
            adresse='123 Rue de Test',
            comptable_traitant=self.comptable,
            client=self.client,
            cree_par=self.user # Assuming 'user' was intended to be 'cree_par'
        )
        self.assertEqual(dossier.denomination, 'Entreprise Test')
        self.assertEqual(dossier.comptable_traitant, self.comptable)
        self.assertEqual(dossier.statut, 'EXISTANT')

    def test_dossier_pm_pp_forfaitaire_properties(self):
        dossier_sarl = Dossier.objects.create(
            code='P',
            denomination='SARL Test',
            forme_juridique='SARL',
            secteur_activites='Informatique',
            branche_activite='Développement',
            adresse='123 Rue de Test',
            comptable_traitant=self.comptable
        )
        self.assertTrue(dossier_sarl.est_pm)
        self.assertFalse(dossier_sarl.est_pp)

        dossier_ei = Dossier.objects.create(
            code='P',
            denomination='EI Test',
            forme_juridique='EI',
            secteur_activites='Informatique',
            branche_activite='Développement',
            adresse='123 Rue de Test',
            comptable_traitant=self.comptable
        )
        self.assertFalse(dossier_ei.est_pm)
        self.assertTrue(dossier_ei.est_pp)

        dossier_forfaitaire = Dossier.objects.create(
            code='F',
            denomination='Forfaitaire Test',
            forme_juridique='EI',
            secteur_activites='Informatique',
            branche_activite='Développement',
            adresse='123 Rue de Test',
            comptable_traitant=self.comptable
        )
        self.assertTrue(dossier_forfaitaire.est_forfaitaire)

    def test_dossier_tva_property(self):
        dossier_mensuel = Dossier.objects.create(
            code='P',
            denomination='TVA Mensuel',
            forme_juridique='SARL',
            secteur_activites='Informatique',
            branche_activite='Développement',
            adresse='123 Rue de Test',
            declaration_tva='MENSUELLE',
            comptable_traitant=self.comptable
        )
        self.assertTrue(dossier_mensuel.a_tva)

        dossier_exonere = Dossier.objects.create(
            code='P',
            denomination='TVA Exonéré',
            forme_juridique='SARL',
            secteur_activites='Informatique',
            branche_activite='Développement',
            adresse='123 Rue de Test',
            declaration_tva='EXONEREE',
            comptable_traitant=self.comptable
        )
        self.assertFalse(dossier_exonere.a_tva)

    def test_dossier_save_status_sync(self):
        dossier_radie = Dossier.objects.create(
            code='R',
            denomination='Radié Test',
            forme_juridique='SARL',
            secteur_activites='Informatique',
            branche_activite='Développement',
            adresse='123 Rue de Test',
            comptable_traitant=self.comptable
        )
        self.assertEqual(dossier_radie.statut, 'RADIE')
        self.assertFalse(dossier_radie.actif)

        dossier_livre = Dossier.objects.create(
            code='L',
            denomination='Livré Test',
            forme_juridique='SARL',
            secteur_activites='Informatique',
            branche_activite='Développement',
            adresse='123 Rue de Test',
            comptable_traitant=self.comptable
        )
        self.assertEqual(dossier_livre.statut, 'LIVRE')
        self.assertFalse(dossier_livre.actif)

        dossier_delaisse = Dossier.objects.create(
            code='D',
            denomination='Délaissé Test',
            forme_juridique='SARL',
            secteur_activites='Informatique',
            branche_activite='Développement',
            adresse='123 Rue de Test',
            comptable_traitant=self.comptable
        )
        self.assertEqual(dossier_delaisse.statut, 'DELAISSE')
        self.assertFalse(dossier_delaisse.actif)

        dossier_existant = Dossier.objects.create(
            code='S',
            denomination='Existant Test',
            forme_juridique='SARL',
            secteur_activites='Informatique',
            branche_activite='Développement',
            adresse='123 Rue de Test',
            comptable_traitant=self.comptable
        )
        self.assertEqual(dossier_existant.statut, 'EXISTANT')
        self.assertTrue(dossier_existant.actif)

    def test_nom_complet_createur_property(self):
        # Test with a user having a comptable_profile
        self.user.comptable_profile = self.comptable
        self.user.save()
        dossier_with_comptable_creator = Dossier.objects.create(
            code='P',
            denomination='Test Dossier',
            forme_juridique='SARL',
            secteur_activites='Informatique',
            branche_activite='Développement',
            adresse='123 Rue de Test',
            comptable_traitant=self.comptable,
            cree_par=self.user
        )
        self.assertEqual(dossier_with_comptable_creator.nom_complet_createur, 'Doe John')

        # Test with a user without a comptable_profile but with first/last name
        user_no_comptable = User.objects.create_user(username='user2', password='password', first_name='Jane', last_name='Smith')
        dossier_with_name_creator = Dossier.objects.create(
            code='P',
            denomination='Test Dossier 2',
            forme_juridique='SARL',
            secteur_activites='Informatique',
            branche_activite='Développement',
            adresse='123 Rue de Test',
            comptable_traitant=self.comptable,
            cree_par=user_no_comptable
        )
        self.assertEqual(dossier_with_name_creator.nom_complet_createur, 'Jane Smith')

        # Test with a user with only username
        user_only_username = User.objects.create_user(username='user3', password='password')
        dossier_with_username_creator = Dossier.objects.create(
            code='P',
            denomination='Test Dossier 3',
            forme_juridique='SARL',
            secteur_activites='Informatique',
            branche_activite='Développement',
            adresse='123 Rue de Test',
            comptable_traitant=self.comptable,
            cree_par=user_only_username
        )
        self.assertEqual(dossier_with_username_creator.nom_complet_createur, 'user3')

        # Test with no creator
        dossier_no_creator = Dossier.objects.create(
            code='P',
            denomination='Test Dossier 4',
            forme_juridique='SARL',
            secteur_activites='Informatique',
            branche_activite='Développement',
            adresse='123 Rue de Test',
            comptable_traitant=self.comptable
        )
        self.assertEqual(dossier_no_creator.nom_complet_createur, '-'
)


