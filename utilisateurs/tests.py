from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Utilisateur, Client

User = get_user_model()

class UtilisateurModelTest(TestCase):
    def test_utilisateur_creation(self):
        user = Utilisateur.objects.create_user(username='testuser', password='password', role='administrateur')
        self.assertEqual(user.username, 'testuser')
        self.assertTrue(user.check_password('password'))
        self.assertEqual(user.role, 'administrateur')

    def test_utilisateur_roles(self):
        admin_user = Utilisateur.objects.create_user(username='admin', password='pass', role='administrateur')
        comptable_user = Utilisateur.objects.create_user(username='comptable', password='pass', role='comptable')
        client_user = Utilisateur.objects.create_user(username='client', password='pass', role='client')

        self.assertTrue(admin_user.is_administrateur())
        self.assertFalse(admin_user.is_comptable())

        self.assertTrue(comptable_user.is_comptable())
        self.assertTrue(comptable_user.is_comptable_prop)

        self.assertTrue(client_user.is_client())

    def test_get_full_name(self):
        user_full_name = Utilisateur.objects.create_user(username='fullnameuser', password='pass', first_name='John', last_name='Doe')
        user_no_name = Utilisateur.objects.create_user(username='nonameuser', password='pass')

        self.assertEqual(user_full_name.get_full_name(), 'John Doe')
        self.assertEqual(user_no_name.get_full_name(), 'nonameuser')

class ClientModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testclientuser', password='password')

    def test_client_creation(self):
        client = Client.objects.create(
            user=self.user,
            contact_personne='Jane Smith',
            email='jane.smith@example.com',
            telephone='1234567890'
        )
        self.assertEqual(client.contact_personne, 'Jane Smith')
        self.assertEqual(client.user, self.user)

    def test_client_str(self):
        client = Client.objects.create(
            user=self.user,
            contact_personne='Jane Smith',
            email='jane.smith@example.com',
            telephone='1234567890'
        )
        self.assertEqual(str(client), f'{self.user.first_name} {self.user.last_name}' if self.user.first_name or self.user.last_name else self.user.username)

        client_no_user = Client.objects.create()
        contact_personne="No User Client",
        email='no.user@example.com',
        telephone='0987654321'
        client_no_user = Client.objects.create(
            contact_personne="No User Client",
            email='no.user@example.com',
            telephone='0987654321'
        )
        self.assertEqual(str(client_no_user), 'No User Client')



