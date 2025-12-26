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
        User = get_user_model()
        username = options['username']
        password = options['password']
        email = options['email']

        try:
            user, created = User.objects.get_or_create(username=username, defaults={
                'email': email,
            })
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
        except Exception as e:
            raise CommandError(f"Échec de création/réinitialisation du superutilisateur: {e}")

