"""
Module applicatif.

Fichier: reclamations/migrations/0002_add_destinataire_field.py
"""

# ==================== Imports ====================
from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings

# ==================== Classes ====================
class Migration(migrations.Migration):
    dependencies = [
        ('reclamations', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='reclamation',
            name='destinataire',
            field=models.ForeignKey(
                to=settings.AUTH_USER_MODEL,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='reclamations_recues',
                verbose_name='Destinataire',
                null=True,
                blank=True
            ),
        ),
    ]