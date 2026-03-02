"""
Définition des routes URL et namespaces.

Fichier: utilisateurs/urls.py
"""

# ==================== Imports ====================
from django.urls import path
from . import views

app_name = 'utilisateurs'

urlpatterns = [
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('register/client/', views.client_register, name='client_register'),
    path('register/comptable/', views.comptable_register, name='comptable_register'),
    path('profile/', views.profile, name='profile'),
    
    # Gestion des clients
    path('clients/', views.liste_clients, name='liste_clients'),
    path('clients/ajouter/', views.ajouter_client_par_admin, name='ajouter_client_par_admin'),
    path('clients/<int:client_id>/', views.detail_client, name='detail_client'),
    path('clients/<int:client_id>/modifier/', views.modifier_client_par_admin, name='modifier_client_admin'),
    path('clients/<int:client_id>/supprimer/', views.supprimer_client, name='supprimer_client'),
]