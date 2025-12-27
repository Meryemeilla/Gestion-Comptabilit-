import sys
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from django.conf import settings

class Command(BaseCommand):
    help = "Crée ou réinitialise un superutilisateur (administrateur) avec les identifiants fournis."

    def add_arguments(self, parser):
        parser.add_argument('--username', required=True, help='Nom d’utilisateur admin à créer ou réinitialiser')
        parser.add_argument('--password', required=True, help='Mot de passe à définir pour le compte admin')
        parser.add_argument('--email', default='admin@example.com', help='Email pour le compte admin')

    def handle(self, *args, **options):
        print("--- STARTING ENSURE_SUPERUSER ---", file=sys.stderr)
        User = get_user_model()
        username = options['username']
        password = options['password']
        email = options['email']

        self.stdout.write(f"--- DEBUG: Starting ensure_superuser for {username} ---")
        try:
            self.stdout.write(f"Checking for user: {username}")

            user, created = User.objects.get_or_create(username=username, defaults={'email': email})
            user.is_staff = True
            user.is_superuser = True
            user.is_active = True
            if hasattr(user, 'role'):
                user.role = 'administrateur'
            if email and not user.email:
                user.email = email
            user.set_password(password)
            user.save()

            if created:
                self.stdout.write(self.style.SUCCESS(f"Superutilisateur '{username}' créé avec succès."))
            else:
                self.stdout.write(self.style.SUCCESS(f"Superutilisateur '{username}' mis à jour avec succès."))

            # Verification
            u = User.objects.get(username=username)
            self.stdout.write(f"--- DEBUG: Verification ---")
            self.stdout.write(f"User: {u.username}")
            self.stdout.write(f"Email: {u.email}")
            self.stdout.write(f"Role: {getattr(u, 'role', 'N/A')}")
            self.stdout.write(f"Is Staff: {u.is_staff}")
            self.stdout.write(f"Is Superuser: {u.is_superuser}")
            self.stdout.write(f"Is Active: {u.is_active}")
            self.stdout.write(f"Has Password: {u.has_usable_password()}")
            if hasattr(u, 'comptable_profile'):
                self.stdout.write(f"Comptable Profile: Exists, Approved={u.comptable_profile.is_approved}")
            else:
                self.stdout.write("Comptable Profile: None")
            self.stdout.write(f"--- DEBUG: Completed ---")

        except Exception as e:
            self.stderr.write(f"--- KEY ERROR ---: {e}")
            raise CommandError(f"Échec de création/réinitialisation du superutilisateur: {e}")
