"""
Enregistrements et personnalisation Admin Django.

Fichier: reclamations/admin.py
"""

# ==================== Imports ====================
from django.contrib import admin
from .models import  Reclamation

@admin.register(Reclamation)
# ==================== Classes ====================
class ReclamationAdmin(admin.ModelAdmin):
    list_display = [
        'code', 'dossier', 'type_reclamation', 'date_reception', 'priorite', 'classement'
    ]
    list_filter = ['code', 'classement', 'priorite', 'date_reception', 'type_reclamation']
    search_fields = ['code','dossier__denomination', 'type_reclamation']
    readonly_fields = ['date_creation', 'date_modification']
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('code','dossier', 'type_reclamation', 'date_reception', 'priorite', 'document')
        }),
        ('Traitement', {
            'fields': ('reponse', 'suivi', 'classement')
        }),
        ('Remarques', {
            'fields': ('remarque',)
        }),
        ('Métadonnées', {
            'fields': ('date_creation', 'date_modification'),
            'classes': ('collapse',)
        }),
    )
