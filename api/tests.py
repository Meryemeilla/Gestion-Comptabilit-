from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from comptables.models import Comptable
from dossiers.models import Dossier

User = get_user_model()

class ComptableAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password', role='administrateur')
        self.client.login(username='testuser', password='password')
        self.comptable_data = {
            'nom': 'Doe',
            'prenom': 'John',
            'email': 'john.doe@example.com'
        }
        self.comptable = Comptable.objects.create(user=self.user, **self.comptable_data)
        self.list_url = reverse('comptable-list')
        self.detail_url = reverse('comptable-detail', kwargs={'pk': self.comptable.pk})

    def test_create_comptable(self):
        new_user = User.objects.create_user(username='newcomptableuser', password='password')
        data = {
            'user': new_user.pk,
            'nom': 'Smith',
            'prenom': 'Jane',
            'email': 'jane.smith@example.com'
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comptable.objects.count(), 2)
        self.assertEqual(Comptable.objects.get(nom='Smith').prenom, 'Jane')

    def test_retrieve_comptable(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['nom'], self.comptable.nom)

    def test_update_comptable(self):
        data = {'nom': 'Doe Updated', 'prenom': 'John', 'email': 'john.doe@example.com', 'user': self.user.pk}
        response = self.client.put(self.detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.comptable.refresh_from_db()
        self.assertEqual(self.comptable.nom, 'Doe Updated')

    def test_delete_comptable(self):
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Comptable.objects.count(), 0)

class DossierAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password', role='administrateur')
        self.client.login(username='testuser', password='password')
        self.comptable = Comptable.objects.create(user=self.user, nom='Doe', prenom='John', email='john.doe@example.com')
        self.dossier_data = {
            'code': 'P',
            'denomination': 'Entreprise Test',
            'forme_juridique': 'SARL',
            'secteur_activites': 'Informatique',
            'branche_activite': 'Développement',
            'adresse': '123 Rue de Test',
            'comptable_traitant': self.comptable.pk
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
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Dossier.objects.count(), 2)
        self.assertEqual(Dossier.objects.get(denomination='Nouvelle Entreprise').forme_juridique, 'SA')

    def test_retrieve_dossier(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['denomination'], self.dossier.denomination)

    def test_update_dossier(self):
        data = {'denomination': 'Entreprise Modifiée', 'code': 'P', 'forme_juridique': 'SARL', 'secteur_activites': 'Informatique', 'branche_activite': 'Développement', 'adresse': '123 Rue de Test', 'comptable_traitant': self.comptable.pk}
        response = self.client.put(self.detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.dossier.refresh_from_db()
        self.assertEqual(self.dossier.denomination, 'Entreprise Modifiée')

    def test_delete_dossier(self):
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Dossier.objects.count(), 0)

