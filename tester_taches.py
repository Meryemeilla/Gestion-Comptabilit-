"""
Script utilitaire pour tester manuellement les tâches Celery.
Exécution : python tester_taches.py
"""
import os
import django
from datetime import date

# Initialisation Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from evenements.tasks import envoyer_voeux_task
from reclamations.tasks import send_rappel_tva_task
from comptables.tasks import send_monthly_reports_task
from evenements.models import Evenement
from utilisateurs.models import Utilisateur, Client
from dossiers.models import Dossier

def setup_test_data():
    print("--- Préparation des données de test ---")
    
    # 1. Événement du jour
    Evenement.objects.get_or_create(
        nom="Test Aujourd'hui",
        defaults={
            'date': date.today(),
            'message': "Joyeux test !",
            'actif': True,
            'type_evenement': 'GREGORIEN'
        }
    )
    
    # 2. Utilisateur & Client Célébrité (pour les vœux)
    user, _ = Utilisateur.objects.get_or_create(
        username="star_client",
        defaults={'email': "star@example.com", 'est_celebrite': True}
    )
    Client.objects.get_or_create(user=user, defaults={'email': "star@example.com", 'contact_personne': "Star"})

    # 3. Dossier en retard (pour la TVA)
    Dossier.objects.get_or_create(
        code="RETARD_TVA",
        defaults={
            'denomination': "Entreprise Retard",
            'statut_fiscal': 'EN_RETARD',
            'dernier_rappel_tva': date(2000, 1, 1) # Très vieux
        }
    )
    print("Données prêtes.\n")

def run_tests():
    print("--- Exécution des tâches ---")
    
    print("\n1. Test des vœux...")
    envoyer_voeux_task()
    
    print("\n2. Test des rappels TVA...")
    send_rappel_tva_task()
    
    print("\n3. Test des rapports mensuels...")
    send_monthly_reports_task()
    
    print("\n--- Tests terminés ---")
    print("Note : Si EMAIL_BACKEND est 'console', vous verrez les emails ci-dessus.")
    print("Si c'est 'smtp', vérifiez votre boîte mail (ou mail.log).")

if __name__ == "__main__":
    setup_test_data()
    run_tests()
