"""
Définition des routes URL et namespaces.

Fichier: utilisateurs/urls.py
"""

# ==================== Imports ====================
from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('register/client/', views.client_register, name='client_register'),
    path('register/comptable/', views.comptable_register, name='comptable_register'),
    path('profile/', views.profile, name='profile'),
]