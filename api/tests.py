"""
Module applicatif.

Fichier: api/tests.py
"""

# ==================== Imports ====================
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from comptables.models import Comptable
from dossiers.models import Dossier
from rest_framework.test import APIClient
User = get_user_model()

# ==================== Classes ====================
class ComptableAPITest(APITestCase):
    def setUp(self):
        self.client_api = APIClient()  # Utiliser APIClient pour DRF
        self.user = User.objects.create_user(username='testuser', password='password', role='administrateur')
        self.client_api.force_authenticate(user=self.user)  # Authentifie pour tous les tests
        self.comptable_data = {'nom': 'Doe', 'prenom': 'John', 'email': 'john.doe@example.com'}
        self.comptable = Comptable.objects.create(user=self.user, **self.comptable_data)
        self.list_url = reverse('comptable-list')
        self.detail_url = reverse('comptable-detail', kwargs={'pk': self.comptable.pk})

    def test_create_comptable(self):
        new_user = User.objects.create_user(username='newcomptableuser', password='password')
        data = {'user': new_user.pk, 'nom': 'Smith', 'prenom': 'Jane', 'email': 'jane.smith@example.com'}
        response = self.client_api.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_retrieve_comptable(self):
        # Utiliser le client DRF authentifié
        response = self.client_api.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['nom'], self.comptable.nom)

    def test_update_comptable(self):
        data = {
            'nom': 'Doe Updated',
            'prenom': 'John',
            'email': 'john.doe@example.com',
            'user': self.user.pk
        }
        response = self.client_api.put(self.detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.comptable.refresh_from_db()
        self.assertEqual(self.comptable.nom, 'Doe Updated')

    def test_delete_comptable(self):
        # Supprimer le comptable avec le client API authentifié
        response = self.client_api.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Vérifier que le comptable supprimé n'existe plus
        exists = Comptable.objects.filter(pk=self.comptable.pk).exists()
        self.assertFalse(exists)



class DossierAPITest(APITestCase):
    def setUp(self):
        self.client_api = APIClient()
        self.user = User.objects.create_user(username='testuser', password='password', role='administrateur')
        self.client_api.force_authenticate(user=self.user)
        self.comptable = Comptable.objects.create(user=self.user, nom='Doe', prenom='John', email='john.doe@example.com')
        self.dossier_data = {
            'code': 'P',
            'denomination': 'Entreprise Test',
            'forme_juridique': 'SARL',
            'secteur_activites': 'Informatique',
            'branche_activite': 'Développement',
            'adresse': '123 Rue de Test'
        }
        self.dossier = Dossier.objects.create(comptable_traitant=self.comptable, **self.dossier_data)
        self.list_url = reverse('dossier-list')
        self.detail_url = reverse('dossier-detail', kwargs={'pk': self.dossier.pk})

    def test_create_dossier(self):
        data = {
            'code': 'S',
            'denomination': 'Nouvelle Entreprise',
            'forme_juridique': 'SA',
            'secteur_activites': 'Finance',
            'branche_activite': 'Audit',
            'adresse': '456 Avenue',
            'comptable_traitant': self.comptable.pk
        }
        response = self.client_api.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_retrieve_dossier(self):
    # Utiliser self.client_api, qui est authentifié
        response = self.client_api.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['denomination'], self.dossier.denomination)


    def test_update_dossier(self):
        data = {
            'denomination': 'Entreprise Modifiée',
            'code': 'P',
            'forme_juridique': 'SARL',
            'secteur_activites': 'Informatique',
            'branche_activite': 'Développement',
            'adresse': '123 Rue de Test',
            'comptable_traitant': self.comptable.pk
        }
        # Utiliser self.client_api plutôt que self.client
        response = self.client_api.put(self.detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.dossier.refresh_from_db()
        self.assertEqual(self.dossier.denomination, 'Entreprise Modifiée')

    def test_delete_dossier(self):
        # Supprimer le dossier avec le client API authentifié
        response = self.client_api.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Vérifier que le dossier supprimé n'existe plus
        exists = Dossier.objects.filter(pk=self.dossier.pk).exists()
        self.assertFalse(exists)



