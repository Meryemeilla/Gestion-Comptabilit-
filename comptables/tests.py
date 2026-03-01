"""
Module applicatif.

Fichier: comptables/tests.py
"""

# ==================== Imports ====================
from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Comptable
from dossiers.models import Dossier
from unittest.mock import patch
from .tasks import send_monthly_reports_task

User = get_user_model()

# ==================== Classes ====================
class ComptableModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testcomptable', password='password')
        self.comptable = Comptable.objects.create(
            user=self.user,
            nom='Dupont',
            prenom='Jean',
            email='jean.dupont@example.com'
        )

    def test_comptable_creation(self):
        self.assertEqual(self.comptable.nom, "Dupont")
        self.assertEqual(self.comptable.prenom, "Jean")
        self.assertEqual(self.comptable.email, "jean.dupont@example.com")
        self.assertTrue(self.comptable.matricule.startswith('COMPT-'))

    def test_comptable_str(self):
        self.assertEqual(str(self.comptable), f'{self.comptable.nom} {self.comptable.prenom} ({self.comptable.matricule})')

    def test_nom_complet_property(self):
        self.assertEqual(self.comptable.nom_complet, "Dupont Jean")

    def test_calculer_statistiques(self):
        # Create some dossiers for the comptable
        Dossier.objects.create(
            code='P', denomination='SARL A', forme_juridique='SARL', secteur_activites='IT', branche_activite='Dev', adresse='123 Rue', comptable_traitant=self.comptable
        )
        Dossier.objects.create(
            code='P', denomination='EI B', forme_juridique='EI', secteur_activites='Consulting', branche_activite='Conseil', adresse='456 Av', comptable_traitant=self.comptable
        )
        Dossier.objects.create(
            code='P', denomination='SARL C', forme_juridique='SARL', secteur_activites='Finance', branche_activite='Audit', adresse='789 Bd', comptable_traitant=self.comptable
        )

        self.comptable.calculer_statistiques()
        self.comptable.refresh_from_db()

        self.assertEqual(self.comptable.nbre_pm, 2)
        self.assertEqual(self.comptable.nbre_et, 1)

    def test_matricule_generation(self):
        new_user = User.objects.create_user(username='testcomptable2', password='password')
        new_comptable = Comptable.objects.create(
            user=new_user,
            nom='Martin',
            prenom='Sophie',
            email='sophie.martin@example.com'
        )
        self.assertTrue(new_comptable.matricule.startswith('COMPT-'))
        self.assertNotEqual(self.comptable.matricule, new_comptable.matricule)

    def test_user_deletion_on_comptable_delete(self):
        user_to_delete = User.objects.create_user(username='user_for_delete', password='password')
        comptable_to_delete = Comptable.objects.create(
            user=user_to_delete,
            nom='Test',
            prenom='Delete',
            email='delete@example.com'
        )
        self.assertTrue(User.objects.filter(username='user_for_delete').exists())
        comptable_to_delete.delete()
        self.assertFalse(User.objects.filter(username='user_for_delete').exists())

class ComptableTaskTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='taskcomptable', password='password')
        self.comptable = Comptable.objects.create(
            user=self.user,
            nom='Task',
            prenom='Tester',
            email='task@example.com'
        )

    @patch('comptables.tasks.send_mail')
    def test_send_monthly_reports_task(self, mock_send_mail):
        # Execute task
        result = send_monthly_reports_task()
        
        # Verify email was sent
        self.assertTrue(mock_send_mail.called)
        self.assertIn("Rapports mensuels envoyés", result)
