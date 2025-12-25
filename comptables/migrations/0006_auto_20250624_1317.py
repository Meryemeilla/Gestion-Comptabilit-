"""
Module applicatif.

Fichier: comptables/migrations/0006_auto_20250624_1317.py
"""

# ==================== Imports ====================
from django.db import migrations, models
from django.conf import settings

# ==================== Fonctions ====================
def create_users_for_comptables(apps, schema_editor):
    Comptable = apps.get_model('comptables', 'Comptable')
    Utilisateur = apps.get_model(settings.AUTH_USER_MODEL.split('.')[0], settings.AUTH_USER_MODEL.split('.')[1])

    for comptable in Comptable.objects.all():
        # Create a new user for each existing comptable
        # You might want to set a default password or handle this more securely
        username = f"comptable_{comptable.matricule}" if comptable.matricule else f"comptable_{comptable.id}"
        email = comptable.email if comptable.email else f"{username}@example.com"
        
        # Ensure username is unique
        original_username = username
        counter = 1
        while Utilisateur.objects.filter(username=username).exists():
            username = f"{original_username}_{counter}"
            counter += 1

        user = Utilisateur.objects.create_user(
            username=username,
            email=email,
            password='default_password_123', # IMPORTANT: Change this in production!
            is_active=True, # Set to active by default
            role='comptable' # Assign the 'comptable' role
        )
        comptable.user = user
        comptable.save()


# ==================== Classes ====================
class Migration(migrations.Migration):

    dependencies = [
        ('comptables', '0005_comptable_tel_personnel'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='comptable',
            name='user',
            field=models.OneToOneField(
                on_delete=models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL,
                null=True, # Temporarily allow null
                blank=True, # Temporarily allow blank
                related_name='comptable_profile'
            ),
        ),
        migrations.RunPython(create_users_for_comptables, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='comptable',
            name='user',
            field=models.OneToOneField(
                on_delete=models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL,
                null=False, # Now make it non-nullable
                blank=False, # Now make it non-blank
                related_name='comptable_profile'
            ),
        ),
    ]
