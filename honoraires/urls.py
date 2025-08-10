from django.urls import path
from .views import (HonoraireCreateView, ReglementHonoraireCreateView, ReglementHonoraireListView, HonorairePVCreateView,
                    ReglementHonorairePVCreateView, HonoraireListView, HonoraireDetailView, HonoraireUpdateView,
                    HonoraireDeleteView, HonorairePVListView, HonorairePVDetailView, HonorairePVUpdateView,
                    HonorairePVDeleteView, HonoraireDashboardView)

app_name = 'honoraires'

urlpatterns = [
    path('dashboard/', HonoraireDashboardView.as_view(), name='honoraire_dashboard'),
    path('', HonoraireListView.as_view(), name='honoraire_list'),
    path('create/', HonoraireCreateView.as_view(), name='honoraire_create'),
    path('reglement/create/', ReglementHonoraireCreateView.as_view(), name='reglement_honoraire_create'),
    path('reglement/', ReglementHonoraireListView.as_view(), name='reglement_list'),
    path('honoraires-pv/', HonorairePVListView.as_view(), name='honoraire_pv_list'),
    path('honoraires-pv/<int:pk>/', HonorairePVDetailView.as_view(), name='honoraire_pv_detail'),
    path('honoraires-pv/create/', HonorairePVCreateView.as_view(), name='honoraire_pv_create'),
    path('honoraires-pv/<int:pk>/update/', HonorairePVUpdateView.as_view(), name='honoraire_pv_update'),
    path('honoraires-pv/<int:pk>/delete/', HonorairePVDeleteView.as_view(), name='honoraire_pv_delete'),
    path('<int:pk>/', HonoraireDetailView.as_view(), name='honoraire_detail'),
    path('<int:pk>/update/', HonoraireUpdateView.as_view(), name='honoraire_update'),
    path('<int:pk>/delete/', HonoraireDeleteView.as_view(), name='honoraire_delete'),
    path('reglement-pv/create/', ReglementHonorairePVCreateView.as_view(), name='reglement_pv_create'),
   ]