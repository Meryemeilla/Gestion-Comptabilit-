"""
Module applicatif.

Fichier: cabinet/tests.py
"""

# ==================== Imports ====================
from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Document, Notification
from dossiers.models import Dossier
from comptables.models import Comptable
User = get_user_model()

# ==================== Classes ====================
class DocumentModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.comptable = Comptable.objects.create(user=self.user, nom='Doe', prenom='John', email='john.doe@example.com')
        self.dossier = Dossier.objects.create(
            code='T',
            denomination='Test Dossier',
            forme_juridique='SARL',
            secteur_activites='Informatique',
            branche_activite='Développement',
            adresse='123 Rue',
            comptable_traitant=self.comptable
        )

    def test_document_creation(self):
        document = Document.objects.create(dossier=self.dossier, nom='Mon Document', fichier='path/to/file.pdf')
        self.assertEqual(document.nom, 'Mon Document')
        self.assertEqual(document.dossier, self.dossier)


class NotificationModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')

    def test_notification_creation(self):
        notification = Notification.objects.create(
            user=self.user, 
            title='Nouveau Message', 
            message='Ceci est un message de test.'
        )
        self.assertEqual(notification.title, 'Nouveau Message')
        self.assertEqual(notification.user, self.user)
        self.assertFalse(notification.read)

    def test_notification_str(self):
        notification = Notification.objects.create(
            user=self.user, 
            title='Nouveau Message', 
            message='Ceci est un message de test.'
        )
        self.assertEqual(str(notification), f'Notification for {self.user}: {notification.title}')
