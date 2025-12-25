"""
Définition des routes URL et namespaces.

Fichier: dossiers/urls.py
"""

# ==================== Imports ====================
from django.urls import path
from . import views

app_name = 'dossiers'

urlpatterns = [
    path('trashed-dossiers/', views.trashed_dossiers, name='trashed_dossiers'),
    path('restore-dossier/<int:pk>/', views.restore_dossier, name='restore_dossier'),
    path('delete-dossier/<int:pk>/', views.delete_dossier, name='delete_dossier'),
    path('corbeille/', views.corbeille_generique, name='corbeille_generique'),
    path('corbeille/<str:model_name>/', views.corbeille_generique, name='corbeille_generique_model'),
    path('restore/<str:model_name>/<int:pk>/', views.restore_item, name='restore_item'),
]