"""
Enregistrements et personnalisation Admin Django.

Fichier: evenements/admin.py
"""

# ==================== Imports ====================
from django.contrib import admin
from .models import Evenement

@admin.register(Evenement)
# ==================== Classes ====================
class EvenementAdmin(admin.ModelAdmin):
    list_display = ('nom', 'date', 'actif')
    list_filter = ('actif', 'date')
    search_fields = ('nom', 'message')

# Register your models here.
