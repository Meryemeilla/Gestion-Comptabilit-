"""
Définition des routes URL et namespaces.

Fichier: juridique/urls.py
"""

# ==================== Imports ====================
from django.urls import path
from cabinet.views import DocumentsClientView
from .views import (
    JuridiqueCreationListView,
    JuridiqueCreationDetailView,
    JuridiqueCreationCreateView,
    JuridiqueCreationUpdateView,
    JuridiqueCreationDeleteView,
    DocumentJuridiqueListView,
    DocumentJuridiqueDetailView,
    DocumentJuridiqueCreateView,
    DocumentJuridiqueUpdateView,
    DocumentJuridiqueDeleteView,
    EvenementJuridiqueListView,
    EvenementJuridiqueDetailView,
    EvenementJuridiqueCreateView,
    EvenementJuridiqueUpdateView,
    EvenementJuridiqueDeleteView,
    dossier_infos_api
)

app_name = 'juridique'

urlpatterns = [
    path('creations/', JuridiqueCreationListView.as_view(), name='juridique_creation_list'),
    path('creations/<int:pk>/', JuridiqueCreationDetailView.as_view(), name='juridique_creation_detail'),
    path('creations/new/', JuridiqueCreationCreateView.as_view(), name='juridique_creation_create'),
    path('api/dossier-infos/', dossier_infos_api, name='dossier_infos_api'),  
    path('creations/<int:pk>/edit/', JuridiqueCreationUpdateView.as_view(), name='juridique_creation_update'),
    path('creations/<int:pk>/delete/', JuridiqueCreationDeleteView.as_view(), name='juridique_creation_delete'),

   

    

    # URLs for DocumentJuridique
    path('documents/', DocumentJuridiqueListView.as_view(), name='documentjuridique_list'),
    path('documents/<int:pk>/', DocumentJuridiqueDetailView.as_view(), name='documentjuridique_detail'),
    path('documents/new/', DocumentJuridiqueCreateView.as_view(), name='documentjuridique_create'),
    path('documents/<int:pk>/edit/', DocumentJuridiqueUpdateView.as_view(), name='documentjuridique_update'),
    path('documents/<int:pk>/delete/', DocumentJuridiqueDeleteView.as_view(), name='documentjuridique_delete'),

    # URLs for EvenementJuridique
    path('evenements/', EvenementJuridiqueListView.as_view(), name='evenementjuridique_list'),
    path('evenements/<int:pk>/', EvenementJuridiqueDetailView.as_view(), name='evenementjuridique_detail'),
    path('evenements/new/', EvenementJuridiqueCreateView.as_view(), name='evenementjuridique_create'),
    path('evenements/<int:pk>/edit/', EvenementJuridiqueUpdateView.as_view(), name='evenementjuridique_update'),
    path('evenements/<int:pk>/delete/', EvenementJuridiqueDeleteView.as_view(), name='evenementjuridique_delete'),
]