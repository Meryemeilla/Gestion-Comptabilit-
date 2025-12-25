"""
Définition des routes URL et namespaces.

Fichier: comptables/urls.py
"""

# ==================== Imports ====================
from django.urls import path
from . import views

app_name = 'comptables'

urlpatterns = [
    path('trash/', views.ComptableTrashListView.as_view(), name='comptable_trash_list'),
]