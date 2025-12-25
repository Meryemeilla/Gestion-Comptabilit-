"""
Modèles Django et logique d’accès aux données.

Fichier: utilisateurs/models.py
"""

# ==================== Imports ====================
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models

# ==================== Classes ====================
class Utilisateur(AbstractUser):
    ROLES = [
        ('administrateur', 'Administrateur'),
        ('comptable', 'Comptable'),
        ('secretaire', 'Secrétaire'),
        ('manager', 'Manager'),
        ('client', 'Client'),
    ]
    role = models.CharField(max_length=20, choices=ROLES, default='client')
    telephone = models.CharField(max_length=20, blank=True, null=True)
    tel_personnel = models.CharField(max_length=20, blank=True, null=True)
    est_celebrite = models.BooleanField(default=False, verbose_name="Est une célébrité")
    groups = models.ManyToManyField(
        Group,
        related_name='utilisateur_set',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='utilisateur_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    @property
    def get_full_name(self):
        if self.first_name or self.last_name:
             return f"{self.first_name} {self.last_name}".strip()
        return self.username
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    def is_administrateur(self):
        return self.role == 'administrateur'

    def is_comptable(self):
        return self.role == 'comptable'

    def is_secretaire(self):
        return self.role == 'secretaire'

    def is_manager(self):
        return self.role == 'manager'

    def is_client(self):
        return self.role == 'client'

    @property
    def is_comptable_prop(self):
        return self.role == 'comptable'

from django.conf import settings 

class Client(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='client_profile',
        null=True,
        blank=True
    )
    nom_entreprise = models.CharField(max_length=200, blank=True, null=True)
    contact_personne = models.CharField(max_length=100)
    email = models.EmailField()
    telephone = models.CharField(max_length=20)
    adresse = models.TextField(blank=True, null=True)
    date_creation = models.DateTimeField(auto_now_add=True)

    @property
    def nom_complet(self):
        """
        Retourne un nom exploitable pour l'affichage du client
        """
        if self.user:
            return f"{self.user.first_name} {self.user.last_name}".strip()
        return self.contact_personne or "Client sans nom"

    
    def __str__(self):
        # Exemple pour afficher prénom et nom du user lié s'il existe
        if self.user:
            return f"{self.user.first_name} {self.user.last_name}"
        # Sinon afficher la personne de contact
        return self.contact_personne




from django.contrib.auth.mixins import UserPassesTestMixin

class RoleRequiredMixin(UserPassesTestMixin):
    allowed_roles = []
    def test_func(self):
        if not self.request.user.is_authenticated:
            return False
        print(f"User role: {self.request.user.role}, Allowed roles: {self.allowed_roles}")
        return self.request.user.role in self.allowed_roles
