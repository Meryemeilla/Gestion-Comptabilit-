"""
Module applicatif.

Fichier: test_voeux.py
"""

# ==================== Imports ====================
import os
import django

# Configurer l'environnement Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from datetime import date
from evenements.models import Evenement
from utilisateurs.models import Utilisateur, Client
from evenements.tasks import envoyer_voeux_task

# 1. Vérifier si l'événement existe déjà, sinon le créer
print("Vérification/création d'un événement pour aujourd'hui...")
try:
    evenement = Evenement.objects.get(nom="Test d'envoi")
    # Mettre à jour la date pour aujourd'hui
    evenement.date = date.today()
    evenement.actif = True
    evenement.save()
    print(f"Événement existant mis à jour: {evenement.nom} pour le {evenement.date}")
except Evenement.DoesNotExist:
    evenement = Evenement.objects.create(
        nom="Test d'envoi",
        date=date.today(),
        message="Ceci est un message de test pour les vœux",
        actif=True,
        type_evenement="GREGORIEN"
    )
    print(f"Nouvel événement créé: {evenement.nom} pour le {evenement.date}")

# 2. Créer un utilisateur avec le champ username
print("\nCréation d'un utilisateur test...")
try:
    user = Utilisateur.objects.get(username='testuser')
    print("Utilisateur existant trouvé")
except Utilisateur.DoesNotExist:
    user = Utilisateur.objects.create_user(
        username='testuser',
        email="test@example.com",
        password="password123",
        first_name="Jean",
        last_name="Dupont",
        est_celebrite=True
    )
    print("Nouvel utilisateur créé")

# 3. Créer un client associé à cet utilisateur
print("\nCréation d'un client test...")
try:
    client = Client.objects.get(user=user)
    print("Client existant trouvé")
except Client.DoesNotExist:
    client = Client.objects.create(
        user=user,
        contact_personne="Client Test",
        email="test@example.com",
        telephone="0123456789"
    )
    print("Nouveau client créé")

# 4. Exécuter la tâche d'envoi d'e-mails
print("\nExécution de la tâche d'envoi d'e-mails...")
envoyer_voeux_task()
print("Tâche terminée. Vérifiez la console pour voir les e-mails envoyés.")