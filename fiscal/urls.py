"""
Définition des routes URL et namespaces.

Fichier: fiscal/urls.py
"""

# ==================== Imports ====================
from django.urls import path
from . import views
from .views import SuiviFiscalListView
from .views import get_suivi_tva_data
from cabinet.util import extraire_infos_identifiants
app_name = 'fiscal'

urlpatterns = [

    path('api/tva/<int:dossier_id>/', get_suivi_tva_data, name='api_get_suivi_tva'),
    

    path('suivi-fiscal/', SuiviFiscalListView.as_view(), name='suivi_fiscal'),
    # SuiviTVA URLs
    path('suivitva/', views.SuiviTVAListView.as_view(), name='suivitva_list'),
    path('suivitva/new/', views.SuiviTVACreateView.as_view(), name='suivitva_create'),
    path('suivitva/<int:pk>/', views.SuiviTVADetailView.as_view(), name='suivitva_detail'),
    path('suivitva/<int:pk>/edit/', views.SuiviTVAUpdateView.as_view(), name='suivitva_update'),
    path('suivitva/<int:pk>/delete/', views.SuiviTVADeleteView.as_view(), name='suivitva_delete'),
    path('fiscal/api/tva/<int:dossier_id>/', views.get_suivi_tva_data),
    path('fiscal/api/tva/<int:dossier_id>/<int:annee>/', views.get_suivi_tva_data),
    
    path('fiscal/api/extrait-infos-pdf/', extraire_infos_identifiants, name='extract_infos_identifiants'),

    # Acompte URLs
    path('acomptes/', views.AcompteListView.as_view(), name='acompte_list'),
    path('acomptes/new/', views.AcompteCreateView.as_view(), name='acompte_create'),
    path('acomptes/<int:pk>/', views.AcompteDetailView.as_view(), name='acompte_detail'),
    path('acomptes/<int:pk>/edit/', views.AcompteUpdateView.as_view(), name='acompte_update'),
    path('acomptes/<int:pk>/delete/', views.AcompteDeleteView.as_view(), name='acompte_delete'),

    # CMIR URLs
    path('cmir/', views.CMIRListView.as_view(), name='cmir_list'),
    path('cmir/new/', views.CMIRCreateView.as_view(), name='cmir_create'),
    path('cmir/<int:pk>/', views.CMIRDetailView.as_view(), name='cmir_detail'),
    path('cmir/<int:pk>/edit/', views.CMIRUpdateView.as_view(), name='cmir_update'),
    path('cmir/<int:pk>/delete/', views.CMIRDeleteView.as_view(), name='cmir_delete'),

    # DepotBilan URLs
    path('depotbilan/', views.DepotBilanListView.as_view(), name='depotbilan_list'),
    path('depotbilan/new/', views.DepotBilanCreateView.as_view(), name='depotbilan_create'),
    path('depotbilan/<int:pk>/', views.DepotBilanDetailView.as_view(), name='depotbilan_detail'),
    path('depotbilan/<int:pk>/edit/', views.DepotBilanUpdateView.as_view(), name='depotbilan_update'),
    path('depotbilan/<int:pk>/delete/', views.DepotBilanDeleteView.as_view(), name='depotbilan_delete'),

    # SuiviForfaitaire URLs
    path('suiviforfaitaire/', views.SuiviForfaitaireListView.as_view(), name='suiviforfaitaire_list'),
    path('suiviforfaitaire/new/', views.SuiviForfaitaireCreateView.as_view(), name='suiviforfaitaire_create'),
    path('suiviforfaitaire/<int:pk>/', views.SuiviForfaitaireDetailView.as_view(), name='suiviforfaitaire_detail'),
    path('suiviforfaitaire/<int:pk>/edit/', views.SuiviForfaitaireUpdateView.as_view(), name='suiviforfaitaire_update'),
    path('suiviforfaitaire/<int:pk>/delete/', views.SuiviForfaitaireDeleteView.as_view(), name='suiviforfaitaire_delete'),
]