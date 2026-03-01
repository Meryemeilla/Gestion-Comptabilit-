"""
Définition des routes URL et namespaces.

Fichier: dossiers/urls.py
"""

# ==================== Imports ====================
from django.urls import path
from . import views

app_name = 'dossiers'

urlpatterns = [
    path('', views.DossierListView.as_view(), name='dossier_list'),
    path('stats/', views.AdminDossierStatsView.as_view(), name='admin_dossier_stats'),
    path('creer/', views.DossierCreateView.as_view(), name='dossier_create'),
    path('<int:pk>/', views.DossierDetailView.as_view(), name='dossier_detail'),
    path('<int:pk>/modifier/', views.DossierUpdateView.as_view(), name='dossier_edit'),
    path('<int:pk>/supprimer/', views.DossierDeleteView.as_view(), name='dossier_delete'),
    path('document/<int:pk>/supprimer/', views.delete_document, name='delete_document'),
    path('assigner/<int:comptable_pk>/<int:dossier_pk>/', views.assign_dossier_to_comptable, name='assign_dossier_to_comptable'),

    path('trashed-dossiers/', views.trashed_dossiers, name='trashed_dossiers'),
    path('restore-dossier/<int:pk>/', views.restore_dossier, name='restore_dossier'),
]