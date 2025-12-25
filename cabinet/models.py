"""
Modèles Django et logique d’accès aux données.

Fichier: cabinet/models.py
"""

# ==================== Imports ====================
from django.db import models
from django.conf import settings
from dossiers.models import Dossier
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()


# ==================== Classes ====================
class Document(models.Model):
    dossier = models.ForeignKey(Dossier, on_delete=models.CASCADE, related_name='documents')
    fichier = models.FileField(upload_to='documents_dossiers/')
    nom = models.CharField(max_length=255, blank=True)
    texte_extrait = models.TextField(blank=True, null=True)
    
    

    def __str__(self):
        return self.nom or self.fichier.name

class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)
    link = models.URLField(blank=True, null=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification for {self.user}: {self.title}"
