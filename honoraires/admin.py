"""
Enregistrements et personnalisation Admin Django.

Fichier: honoraires/admin.py
"""

# ==================== Imports ====================
from django.contrib import admin
from django.contrib import admin
from .models import Honoraire, ReglementHonoraire, HonorairePV


# ==================== Classes ====================
class ReglementHonoraireInline(admin.TabularInline):
    model = ReglementHonoraire
    extra = 0
    readonly_fields = ['date_creation']


@admin.register(Honoraire)
class HonoraireAdmin(admin.ModelAdmin):
    list_display = [
        'code','dossier', 'montant_mensuel', 'montant_trimestriel', 'montant_annuel',
        'reste_mensuel', 'reste_trimestriel', 'reste_annuel'
    ]
    list_filter = ['code','date_creation']

    search_fields = ['code','dossier__denomination', 'dossier__comptable_traitant__nom']
    readonly_fields = ['date_creation', 'date_modification']
    inlines = [ReglementHonoraireInline]
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('dossier', 'dossier__comptable_traitant')


@admin.register(ReglementHonoraire)
class ReglementHonoraireAdmin(admin.ModelAdmin):
    list_display = [
        'honoraire', 'date_reglement', 'montant', 'type_reglement', 'mode_paiement'
    ]
    list_filter = ['type_reglement', 'mode_paiement', 'date_reglement']
    search_fields = ['honoraire__dossier__denomination', 'numero_piece']
    readonly_fields = ['date_creation', 'date_modification']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('honoraire__dossier')


# class ReglementHonorairePVInline(admin.TabularInline):
#     model = ReglementHonorairePV
#     extra = 0


@admin.register(HonorairePV)
class HonorairePVAdmin(admin.ModelAdmin):
    list_display = ['code','dossier', 'montant_total', 'total_reglements_pv', 'reste_pv']
    inlines = [ReglementHonoraireInline]


# @admin.register(ReglementHonorairePV)
# class ReglementHonorairePVAdmin(admin.ModelAdmin):
#     list_display = ['honoraire_pv', 'date_reglement', 'montant', 'type_reglement']


