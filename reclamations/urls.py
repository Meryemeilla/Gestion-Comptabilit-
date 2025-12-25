"""
Définition des routes URL et namespaces.

Fichier: reclamations/urls.py
"""

# ==================== Imports ====================
from django.urls import path
from . import views

app_name = 'reclamations'

urlpatterns = [
    path('create/', views.create, name='create'),
]