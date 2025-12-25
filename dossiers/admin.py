"""
Enregistrements et personnalisation Admin Django.

Fichier: dossiers/admin.py
"""

# ==================== Imports ====================
from django.contrib import admin

from .models import Dossier


@admin.register(Dossier)
# ==================== Classes ====================
class DossierAdmin(admin.ModelAdmin):
    list_display = [
        'denomination', 'code', 'forme_juridique', 'declaration_tva',
        'comptable_traitant', 'statut', 'actif', 'date_creation'
    ]
    list_filter = [
        'code', 'forme_juridique', 'declaration_tva', 'statut', 
        'actif', 'comptable_traitant', 'date_creation'
    ]
    search_fields = [
        'denomination', 'abreviation', 'ice', 'rc', 'if_identifiant'
    ]
    readonly_fields = ['date_creation_dossier', 'date_modification']
    
    fieldsets = (
        ('Informations de base', {
            'fields': (
                'code', 'denomination', 'abreviation',
                'forme_juridique', 'date_creation', 'secteur_activites', 'branche_activite'
            )
        }),
        ('Coordonnées', {
            'fields': ('adresse', 'email', 'fixe', 'gsm')
        }),
        ('Personnes de contact', {
            'fields': ('gerant', 'personne_a_contacter')
        }),
        ('Identifiants officiels', {
            'fields': ('if_identifiant', 'ice', 'tp', 'rc', 'cnss'),
            'classes': ('collapse',)
        }),
        ('TVA et gestion', {
            'fields': ('declaration_tva', 'comptable_traitant', 'statut', 'actif')
        }),
        ('Métadonnées', {
            'fields': ('date_creation_dossier', 'date_modification'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('comptable_traitant')

