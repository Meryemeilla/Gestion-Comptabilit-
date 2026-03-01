"""
Définition des routes URL et namespaces.

Fichier: cabinet/urls.py
"""

# ==================== Imports ====================
from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views
from cabinet.views_api import analyser_document_view
from .views import preview_identifiants_ajax
from .views import home_view, custom_logout
app_name = 'cabinet'

urlpatterns = [
    # Page d'accueil et tableau de bord
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    # Les stats de dossiers sont maintenant dans l'app dossiers
    path('accounts/logout/', custom_logout, name='logout'),
    
    path('accueil/', home_view, name='home'),
    
    # Les comptables sont maintenant gérés dans l'app comptables
    
    # Les dossiers sont maintenant gérés dans l'app dossiers

    
    # Gestion des honoraires
    path('fiscal/', include('fiscal.urls', namespace='fiscal')),
    path('export/honoraires-pv/', views.export_honoraires_pv, name='export_honoraires_pv'),
    

   
    path('api/analyser-document/', analyser_document_view, name='analyser_document'),
    path('fiscal/ajax/preview-identifiants/', preview_identifiants_ajax, name='preview_identifiants_ajax'),

    
    # Les suivis fiscaux sont maintenant gérés dans l'app fiscal
    
    # Réclamations
    # Les réclamations sont maintenant gérées dans l'app reclamations

    path('mon-compte/modifier-mot-de-passe/', auth_views.PasswordChangeView.as_view(
        template_name='registration/password_change_form.html',
        success_url='/mon-compte/modifier-mot-de-passe/succes/'
    ), name='password_change'),

    path('mon-compte/modifier-mot-de-passe/succes/', auth_views.PasswordChangeDoneView.as_view(
        template_name='registration/password_change_done.html'
    ), name='password_change_done'),
    
    # Les clients sont maintenant gérés dans l'app utilisateurs
    # Juridique est maintenant géré dans l'app juridique

    path('juridique/', include('juridique.urls', namespace='juridique')),
    
    # Rapports et exports
    path('rapports/', views.RapportsView.as_view(), name='rapports'),
    path('export/excel/<str:type>/', views.ExportExcelView.as_view(), name='export_excel'),
    path('export/acomptes/', views.export_acomptes, name='export_acomptes'),
    path('export/pdf/<str:type>/', views.ExportPDFView.as_view(), name='export_pdf'),

    
    

    

    # Emails
    path('email/send/', views.SendEmailView.as_view(), name='send_email'),
]

