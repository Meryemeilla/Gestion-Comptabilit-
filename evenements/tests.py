"""
Module applicatif.

Fichier: evenements/tests.py
"""

# ==================== Imports ====================
from django.test import TestCase
from datetime import date
from django.utils import timezone
from unittest.mock import patch, MagicMock
from .models import Evenement
from .tasks import envoyer_voeux_task
from .tasks_update_dates import update_event_dates_annually

# ==================== Classes ====================
class EvenementTaskTest(TestCase):
    def setUp(self):
        self.evenement = Evenement.objects.create(
            nom="NEW_YEAR_GREGORIAN",
            date=timezone.localdate(),
            type_evenement='GREGORIEN'
        )

    @patch('evenements.tasks.get_celebrite_clients')
    @patch('evenements.tasks.get_celebrite_comptables')
    @patch('evenements.tasks.EmailService')
    def test_envoyer_voeux_task(self, mock_email_service, mock_comptables, mock_clients):
        # Mocking data
        mock_client = MagicMock()
        mock_client.nom_complet = "Client Test"
        mock_client.email = "client@test.com"
        mock_clients.return_value = [mock_client]
        
        mock_comptable = MagicMock()
        mock_comptable.nom_complet = "Comptable Test"
        mock_comptable.email = "comptable@test.com"
        mock_comptables.return_value = [mock_comptable]
        
        # Execute task
        envoyer_voeux_task()
        
        # Verify email service was called
        self.assertEqual(mock_email_service.return_value.send_email.call_count, 2)

    @patch('evenements.tasks_update_dates.holidays.FR')
    @patch('evenements.tasks_update_dates.holidays.MA')
    def test_update_event_dates_annually(self, mock_holidays_ma, mock_holidays_fr):
        # Mocking holidays
        mock_holidays_fr.return_value.items.return_value = [(date(2025, 1, 1), "Nouvel An")]
        mock_holidays_ma.return_value.items.return_value = [(date(2025, 5, 1), "Fête du Travail")]
        
        # Execute task
        update_event_dates_annually()
        
        # Verify events were created
        self.assertTrue(Evenement.objects.filter(nom="Nouvel An").exists())
        self.assertTrue(Evenement.objects.filter(nom="Fête du Travail").exists())
