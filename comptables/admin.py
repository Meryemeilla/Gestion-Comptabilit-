"""
Enregistrements et personnalisation Admin Django.

Fichier: comptables/admin.py
"""

# ==================== Imports ====================
from django.contrib import admin


from .models import Comptable


@admin.register(Comptable)
# ==================== Classes ====================
class ComptableAdmin(admin.ModelAdmin):
    list_display = [
        'matricule', 'nom', 'prenom', 'email', 'tel', 
        'nbre_pm', 'nbre_et', 'actif', 'is_approved', 'date_creation'
    ]
    list_filter = ['actif', 'is_approved', 'date_creation']
    search_fields = ['matricule', 'nom', 'prenom', 'email']
    readonly_fields = ['nbre_pm', 'nbre_et', 'nbre_personn', 'nbre_bureau', 'date_creation', 'date_modification']
    
    fieldsets = (
        ('Informations personnelles', {
            'fields': ('user', 'matricule', 'nom', 'prenom', 'cnss', 'is_approved')
        }),
        ('Contact', {
            'fields': ('tel', 'tel_personnel', 'email', 'email_personnel', 'adresse')
        }),
        ('Statistiques', {
            'fields': ('nbre_pm', 'nbre_et', 'nbre_personn', 'nbre_bureau'),
            'classes': ('collapse',)
        }),
        ('Métadonnées', {
            'fields': ('actif', 'date_creation', 'date_modification'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['calculer_statistiques']
    
    def calculer_statistiques(self, request, queryset):
        for comptable in queryset:
            comptable.calculer_statistiques()
        self.message_user(request, f"Statistiques recalculées pour {queryset.count()} comptables.")
    calculer_statistiques.short_description = "Recalculer les statistiques"


