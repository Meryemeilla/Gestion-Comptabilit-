"""
Définition des routes URL et namespaces.

Fichier: reclamations/urls.py
"""

# ==================== Imports ====================
from django.urls import path
from . import views

app_name = 'reclamations'

urlpatterns = [
    path('', views.ReclamationListView.as_view(), name='reclamation_list'),
    path('creer/', views.ReclamationCreateView.as_view(), name='reclamation_create'),
    path('<int:pk>/', views.ReclamationDetailView.as_view(), name='reclamation_detail'),
    path('<int:pk>/modifier/', views.ReclamationUpdateView.as_view(), name='reclamation_update'),
    path('<int:pk>/supprimer/', views.ReclamationDeleteView.as_view(), name='reclamation_delete'),
    path('trash/', views.ReclamationTrashListView.as_view(), name='reclamation_trash_list'),
    path('<int:pk>/restaurer/', views.reclamation_restore, name='reclamation_restore'),
    path('test/reclamation/<int:reclamation_id>/', views.lancer_tache_reclamation, name='test_reclamation'),
]