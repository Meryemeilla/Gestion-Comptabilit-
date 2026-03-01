# ==================== Imports ====================
from django.test import TestCase
from django.contrib.auth import get_user_model
from dossiers.models import Dossier
from comptables.models import Comptable
from .models import Reclamation
from datetime import date
from unittest.mock import patch
from .tasks import send_rappel_tva_task

User = get_user_model()

# ==================== Classes ====================
class ReclamationModelTest(TestCase):
    def setUp(self):
        self.user_admin = User.objects.create_user(username='reclamation_admin', password='password', role='administrateur')
        self.user_comptable = User.objects.create_user(username='reclamation_comptable', password='password', role='comptable')
        
        self.comptable = Comptable.objects.create(
            user=self.user_comptable,
            nom='Test',
            prenom='Comptable',
            email='test@example.com'
        )
        
        self.dossier = Dossier.objects.create(
            code='P',
            denomination='Client A',
            forme_juridique='SARL',
            secteur_activites='Commerce',
            branche_activite='Vente',
            adresse='123 Rue',
            comptable_traitant=self.comptable
        )
        
        self.reclamation = Reclamation.objects.create(
            dossier=self.dossier,
            code='REC-001',
            type_reclamation='Retard TVA',
            date_reception=date.today(),
            destinataire=self.user_comptable,
            created_by=self.user_admin
        )

    def test_reclamation_creation(self):
        self.assertEqual(self.reclamation.code, 'REC-001')
        self.assertEqual(self.reclamation.type_reclamation, 'Retard TVA')
        self.assertEqual(self.reclamation.classement, 'EN_COURS')
        self.assertEqual(self.reclamation.priorite, 'NORMALE')

    def test_reclamation_str(self):
        expected_str = f"Réclamation Retard TVA - {self.dossier.denomination}"
        self.assertEqual(str(self.reclamation), expected_str)

    def test_soft_delete(self):
        # Test default objects manager
        self.assertTrue(Reclamation.objects.filter(pk=self.reclamation.pk).exists())
        
        # Soft delete
        self.reclamation.delete()
        self.assertTrue(self.reclamation.is_deleted)
        
        # Default manager should filter it out
        self.assertFalse(Reclamation.objects.filter(pk=self.reclamation.pk).exists())
        
        # all_objects should still find it
        self.assertTrue(Reclamation.all_objects.filter(pk=self.reclamation.pk).exists())

    def test_restore(self):
        self.reclamation.delete()
        self.assertTrue(self.reclamation.is_deleted)
        
        self.reclamation.restore()
        self.assertFalse(self.reclamation.is_deleted)
        self.assertTrue(Reclamation.objects.filter(pk=self.reclamation.pk).exists())

class ReclamationTaskTest(TestCase):
    def setUp(self):
        self.user_comptable = User.objects.create_user(username='task_comptable', password='password', role='comptable')
        self.comptable = Comptable.objects.create(
            user=self.user_comptable,
            nom='Tester',
            prenom='Task',
            email='task@example.com'
        )
        self.dossier = Dossier.objects.create(
            code='P',
            denomination='Client Overdue',
            forme_juridique='SARL',
            secteur_activites='Commerce',
            adresse='No Way',
            comptable_traitant=self.comptable,
            statut_fiscal='EN_RETARD',
            dernier_rappel_tva=date(2000, 1, 1) # Long ago
        )

    @patch('reclamations.tasks.EmailService')
    def test_send_rappel_tva_task(self, mock_email_service):
        # Configure mock
        mock_email_service.return_value.send_rappel_tva.return_value = True
        
        # Execute task
        result = send_rappel_tva_task()
        
        # Verify
        self.assertTrue(result)
        self.assertTrue(mock_email_service.return_value.send_rappel_tva.called)
        
        # Verify dossier was updated
        self.dossier.refresh_from_db()
        self.assertEqual(self.dossier.dernier_rappel_tva, date.today())
