from django.urls import path
from . import views

app_name = 'dossiers'

urlpatterns = [ 
    path('client/', views.client_dossiers, name='client_dossiers'),
]