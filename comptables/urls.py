"""
Définition des routes URL et namespaces.

Fichier: comptables/urls.py
"""

# ==================== Imports ====================
from django.urls import path
from . import views

app_name = 'comptables'

urlpatterns = [
    path('', views.ComptableListView.as_view(), name='comptable_list'),
    path('create/', views.ComptableCreateView.as_view(), name='comptable_create'),
    path('<int:pk>/', views.ComptableDetailView.as_view(), name='comptable_detail'),
    path('<int:pk>/edit/', views.ComptableUpdateView.as_view(), name='comptable_edit'),
    path('<int:pk>/delete/', views.ComptableDeleteView.as_view(), name='comptable_delete'),
    path('trash/', views.ComptableTrashListView.as_view(), name='comptable_trash_list'),
]