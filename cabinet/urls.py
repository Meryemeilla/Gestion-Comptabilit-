"""
Définition des routes URL et namespaces.

Fichier: cabinet/urls.py
"""

# ==================== Imports ====================
from django.urls import path, include
from . import views
from .views import FiscalDocumentRedirectView
from .views import lancer_tache_rappel_tva, lancer_tache_reclamation
from django.contrib.auth import views as auth_views
from cabinet.views_api import analyser_document_view
from .views import preview_identifiants_ajax
from .views import home_view, custom_logout
from comptables.views import ComptableActiveListView
app_name = 'cabinet'

urlpatterns = [
    # Page d'accueil et tableau de bord
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('admin-dossier-stats/', views.AdminDossierStatsView.as_view(), name='admin_dossier_stats'),
    path('accounts/logout/', custom_logout, name='logout'),
    
    path('accueil/', home_view, name='home'),

    path('register/client/', views.client_register, name='client_register'),
    
    # Gestion des comptables
    path('comptables/', ComptableActiveListView.as_view(), name='comptable_list'),
    path('comptables/create/', views.ComptableCreateView.as_view(), name='comptable_create'),
    path('comptables/<int:pk>/', views.ComptableDetailView.as_view(), name='comptable_detail'),
    path('comptables/<int:pk>/edit/', views.ComptableUpdateView.as_view(), name='comptable_edit'),
    path('comptables/<int:pk>/delete/', views.ComptableDeleteView.as_view(), name='comptable_delete'),
    
    path('document/<int:pk>/delete/', views.delete_document, name='delete_document'),
    # Gestion des dossiers
    path('dossiers/', views.DossierListView.as_view(), name='dossier_list'),
    path('dossiers/create/', views.DossierCreateView.as_view(), name='dossier_create'),
    path('dossiers/<int:pk>/', views.DossierDetailView.as_view(), name='dossier_detail'),
    path('dossiers/<int:pk>/edit/', views.DossierUpdateView.as_view(), name='dossier_edit'),
    path('dossiers/<int:pk>/delete/', views.DossierDeleteView.as_view(), name='dossier_delete'),
    path('dossiers/trash/', views.DossierTrashListView.as_view(), name='dossier_trash_list'),
    path('dossiers/<int:pk>/restore/', views.dossier_restore, name='dossier_restore'),
    path('comptables/<int:comptable_pk>/assign_dossier/<int:dossier_pk>/', views.assign_dossier_to_comptable, name='assign_dossier_to_comptable'),

    
    # Gestion des honoraires
    path('fiscal/', include('fiscal.urls', namespace='fiscal')),
    path('export/honoraires-pv/', views.export_honoraires_pv, name='export_honoraires_pv'),
    

   
    path('api/analyser-document/', analyser_document_view, name='analyser_document'),
    path('fiscal/ajax/preview-identifiants/', preview_identifiants_ajax, name='preview_identifiants_ajax'),

    
    # Suivi TVA
    path('suivi-tva/', views.SuiviTVAListView.as_view(), name='suivi_tva_list'),
    path('suivi-tva/<int:pk>/', views.SuiviTVADetailView.as_view(), name='suivi_tva_detail'),
    path('suivi-tva/<int:pk>/edit/', views.SuiviTVAUpdateView.as_view(), name='suivi_tva_edit'),
    path('suivi-tva/create/', views.SuiviTVACreateView.as_view(), name='fiscal_create'),
    path('forfaitaire/create/', views.SuiviForfaitaireCreateView.as_view(), name='forfaitaire_create'),
    path('acompte/create/', views.AcompteCreateView.as_view(), name='acompte_create'),
    path('cmir/create/', views.CMIRCreateView.as_view(), name='cmir_create'),
    path('depotbilan/create/', views.DepotBilanCreateView.as_view(), name='depotbilan_create'),
    path('fiscal/document-redirect/', FiscalDocumentRedirectView.as_view(), name='fiscal_document_redirect'),
    
    # Réclamations
    path('reclamations/', views.ReclamationListView.as_view(), name='reclamation_list'),
    path('reclamations/<int:pk>/', views.ReclamationDetailView.as_view(), name='reclamation_detail'),
    path('reclamations/create/', views.ReclamationCreateView.as_view(), name='reclamation_create'),
    path('reclamations/<int:pk>/update/', views.ReclamationUpdateView.as_view(), name='reclamation_update'),
    path('reclamations/<int:pk>/delete/', views.ReclamationDeleteView.as_view(), name='reclamation_delete'),
    path('reclamations/trash/', views.ReclamationTrashListView.as_view(), name='reclamation_trash_list'),
    path('reclamations/<int:pk>/restore/', views.reclamation_restore, name='reclamation_restore'),
    path('reclamations/<int:pk>/ajouter-suivi/', views.reclamation_add_suivi, name='reclamation_add_suivi'),

    path('mon-compte/modifier-mot-de-passe/', auth_views.PasswordChangeView.as_view(
        template_name='registration/password_change_form.html',
        success_url='/mon-compte/modifier-mot-de-passe/succes/'
    ), name='password_change'),

    path('mon-compte/modifier-mot-de-passe/succes/', auth_views.PasswordChangeDoneView.as_view(
        template_name='registration/password_change_done.html'
    ), name='password_change_done'),
    
    path('clients/', views.liste_clients, name='liste_clients'),
    path('modifier/<int:client_id>/', views.modifier_client_par_admin, name='modifier_client_par_admin'),
    path('clients/supprimer/<int:client_id>/', views.supprimer_client, name='supprimer_client'),
    path('clients/detail/<int:client_id>/', views.detail_client, name='detail_client'), 

    path('ajouter-par-admin/', views.ajouter_client_par_admin, name='ajouter_client_par_admin'),
    # Juridique
    path('juridique/', views.JuridiqueListView.as_view(), name='juridique_list'),
    path('juridique/create/', views.JuridiqueCreateView.as_view(), name='juridique_create'),
    path('juridique/<int:pk>/', views.JuridiqueDetailView.as_view(), name='juridique_detail'),

    path('juridique/', include('juridique.urls', namespace='juridique')),
    
    # Rapports et exports
    path('rapports/', views.RapportsView.as_view(), name='rapports'),
    path('export/excel/<str:type>/', views.ExportExcelView.as_view(), name='export_excel'),
    path('export/acomptes/', views.export_acomptes, name='export_acomptes'),
    path('export/pdf/<str:type>/', views.ExportPDFView.as_view(), name='export_pdf'),

    
    

    

    path('test/rappel-tva/', lancer_tache_rappel_tva, name='test_rappel_tva'),
    path('test/reclamation/<int:reclamation_id>/', lancer_tache_reclamation, name='test_reclamation'),
    # Emails
    path('email/send/', views.SendEmailView.as_view(), name='send_email'),
]

