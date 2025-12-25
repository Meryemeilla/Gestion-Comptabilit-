"""
Enregistrements et personnalisation Admin Django.

Fichier: fiscal/admin.py
"""

# ==================== Imports ====================
from django.contrib import admin

from django.contrib import admin
from .models import SuiviTVA, Acompte, CMIR, DepotBilan, SuiviForfaitaire


@admin.register(SuiviTVA)
# ==================== Classes ====================
class SuiviTVAAdmin(admin.ModelAdmin):
    list_display = [
        'code','dossier', 'annee', 'pourcentage_mensuel_complete', 'pourcentage_trimestriel_complete'
    ]
    list_filter = ['code','annee', 'dossier__declaration_tva']
    search_fields = ['dossier__denomination']
    readonly_fields = ['date_creation', 'date_modification']
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('dossier', 'annee')
        }),
        ('Suivi mensuel', {
            'fields': (
                ('jan', 'fev', 'mars'),
                ('avril', 'mai', 'juin'),
                ('juillet', 'aout', 'sep'),
                ('oct', 'nov', 'dec')
            )
        }),
        ('Suivi trimestriel', {
            'fields': (('t1', 't2', 't3', 't4'),)
        }),
        ('Métadonnées', {
            'fields': ('date_creation', 'date_modification'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Acompte)
class AcompteAdmin(admin.ModelAdmin):
    list_display = [
        'code','dossier', 'annee', 'is_montant', 'total_acomptes', 'regularisation'
    ]
    list_filter = ['code','annee']
    search_fields = ['dossier__denomination']
    readonly_fields = ['date_creation', 'date_modification']


@admin.register(CMIR)
class CMIRAdmin(admin.ModelAdmin):
    list_display = [
        'code','dossier', 'annee', 'montant_ir', 'montant_cm', 'complement_ir'
    ]
    list_filter = ['code','annee']
    search_fields = ['dossier__denomination']
    readonly_fields = ['date_creation', 'date_modification']


@admin.register(DepotBilan)
class DepotBilanAdmin(admin.ModelAdmin):
    list_display = [
        'code','dossier', 'annee_exercice', 'date_depot', 'statut'
    ]
    list_filter = ['code','statut', 'annee_exercice']
    search_fields = ['dossier__denomination']
    readonly_fields = ['date_creation', 'date_modification']


@admin.register(SuiviForfaitaire)
class SuiviForfaitaireAdmin(admin.ModelAdmin):
    list_display = [
        'code',
        'dossier',
        'annee',
        'code',
        'pp',
        'paiement_annuel',
        'ir',
        'code_9421',  # Si renommé dans le modèle
        'acompte_1',
        'acompte_2',
        'acompte_3',
        'acompte_4',
        'date_creation',
        'date_modification',
    ]
    list_filter = ['code','annee', 'dossier']

    search_fields = ['dossier__denomination', 'code', 'pp', 'ir', 'code_9421']

    # Méthodes pour formater l'affichage des acomptes
    def get_acompte_1(self, obj):
        return f"{obj.acompte_1:.2f} €" if obj.acompte_1 else "-"
    get_acompte_1.short_description = "1er Acompte"

    def get_acompte_2(self, obj):
        return f"{obj.acompte_2:.2f} €" if obj.acompte_2 else "-"
    get_acompte_2.short_description = "2ème Acompte"

    def get_acompte_3(self, obj):
        return f"{obj.acompte_3:.2f} €" if obj.acompte_3 else "-"
    get_acompte_3.short_description = "3ème Acompte"

    def get_acompte_4(self, obj):
        return f"{obj.acompte_4:.2f} €" if obj.acompte_4 else "-"
    get_acompte_4.short_description = "4ème Acompte"

    # Filtres et recherche
   

    readonly_fields = [
        'date_creation', 
        'date_modification',
        'get_total_acomptes'
    ]

    fieldsets = (
        ('Informations de base', {
            'fields': ('dossier', 'annee','code', 'pp')
        }),
        ('Déclarations et Paiements', {
            'fields': (
                'paiement_annuel',
                ('acompte_1', 'acompte_2', 'acompte_3', 'acompte_4'),
                'get_total_acomptes'
            )
        }),
       
    )

    # Ajout d'un calcul de total des acomptes
    def get_total_acomptes(self, obj):
        total = sum([obj.acompte_1 or 0, 
                    obj.acompte_2 or 0, 
                    obj.acompte_3 or 0, 
                    obj.acompte_4 or 0])
        return f"{total:.2f} €"
    get_total_acomptes.short_description = "Total Acomptes"

    
    
   
