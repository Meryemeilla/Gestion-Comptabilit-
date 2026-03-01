"""
Module applicatif.

Fichier: api/tests.py
"""

# ==================== Imports ====================
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from comptables.models import Comptable
from dossiers.models import Dossier
from honoraires.models import Honoraire
from fiscal.models import SuiviTVA
from reclamations.models import Reclamation

User = get_user_model()

# ==================== Classes ====================
class ComptableAPITest(APITestCase):
    def setUp(self):
        self.client_api = APIClient()
        self.user = User.objects.create_user(username='api_comptable_user', password='password', role='administrateur')
        self.client_api.force_authenticate(user=self.user)
        self.comptable = Comptable.objects.create(user=self.user, nom='Doe', prenom='John', email='john@example.com')
        self.list_url = reverse('comptable-list')
        self.detail_url = reverse('comptable-detail', kwargs={'pk': self.comptable.pk})

    def test_list_comptables(self):
        response = self.client_api.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_comptable(self):
        response = self.client_api.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

class DossierAPITest(APITestCase):
    def setUp(self):
        self.client_api = APIClient()
        self.user = User.objects.create_user(username='api_dossier_user', password='password', role='administrateur')
        self.client_api.force_authenticate(user=self.user)
        self.comptable = Comptable.objects.create(user=self.user, nom='Doe', prenom='John', email='john@example.com')
        self.dossier = Dossier.objects.create(
            denomination='Entreprise Test',
            code='P',
            forme_juridique='SARL',
            secteur_activites='IT',
            comptable_traitant=self.comptable,
            adresse='Test Address'
        )
        self.list_url = reverse('dossier-list')
        self.detail_url = reverse('dossier-detail', kwargs={'pk': self.dossier.pk})

    def test_list_dossiers(self):
        response = self.client_api.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

class HonoraireAPITest(APITestCase):
    def setUp(self):
        self.client_api = APIClient()
        self.user = User.objects.create_user(username='api_honoraire_user', password='password', role='administrateur')
        self.client_api.force_authenticate(user=self.user)
        self.comptable = Comptable.objects.create(user=self.user, nom='Doe', prenom='John', email='john@example.com')
        self.dossier = Dossier.objects.create(denomination='Dossier H', code='P', forme_juridique='SARL', adresse='Addr', comptable_traitant=self.comptable)
        self.honoraire = Honoraire.objects.create(dossier=self.dossier, montant_annuel=12000)
        self.list_url = reverse('honoraire-list')

    def test_list_honoraires(self):
        response = self.client_api.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

class SuiviTVAAPITest(APITestCase):
    def setUp(self):
        self.client_api = APIClient()
        self.user = User.objects.create_user(username='api_tva_user', password='password', role='administrateur')
        self.client_api.force_authenticate(user=self.user)
        self.comptable = Comptable.objects.create(user=self.user, nom='Doe', prenom='John', email='john@example.com')
        self.dossier = Dossier.objects.create(denomination='Dossier T', code='P', forme_juridique='SARL', adresse='Addr', comptable_traitant=self.comptable)
        self.suivi = SuiviTVA.objects.create(dossier=self.dossier, annee=2024)
        self.list_url = reverse('suivitva-list')

    def test_list_suivi_tva(self):
        response = self.client_api.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

class ReclamationAPITest(APITestCase):
    def setUp(self):
        self.client_api = APIClient()
        self.user = User.objects.create_user(username='api_reclamation_user', password='password', role='administrateur')
        self.client_api.force_authenticate(user=self.user)
        self.comptable = Comptable.objects.create(user=self.user, nom='Doe', prenom='John', email='john@example.com')
        self.dossier = Dossier.objects.create(denomination='Dossier R', code='P', forme_juridique='SARL', adresse='Addr', comptable_traitant=self.comptable)
        self.reclamation = Reclamation.objects.create(dossier=self.dossier, type_reclamation='Test', date_reception='2024-01-01', created_by=self.user)
        self.list_url = reverse('reclamation-list')

    def test_list_reclamations(self):
        response = self.client_api.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
