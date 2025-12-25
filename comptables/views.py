"""
Django views (gestion des requêtes HTTP).

Fichier: comptables/views.py
"""

# ==================== Imports ====================
from django.shortcuts import render
from django.views.generic import ListView
from comptables.models import Comptable

# ==================== Handlers ====================
class ComptableActiveListView(ListView):
    model = Comptable
    template_name = 'comptables/list.html'
    context_object_name = 'comptables'

    def get_queryset(self):
        return Comptable.objects.filter(is_deleted=False)

class ComptableTrashListView(ListView):
    model = Comptable
    template_name = 'comptables/list.html'  # Use the same list template
    context_object_name = 'comptables'

    def get_queryset(self):
        return Comptable.objects.filter(is_deleted=True)
