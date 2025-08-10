from django.shortcuts import render
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .viewsets import (
    ComptableViewSet,
    DossierViewSet,
    HonoraireViewSet,
    ReglementHonoraireViewSet,
    SuiviTVAViewSet,
    ReclamationViewSet,
    StatistiquesViewSet,
)

# Configuration du routeur DRF
router = DefaultRouter()
router.register(r'comptables', ComptableViewSet)
router.register(r'dossiers', DossierViewSet)
router.register(r'honoraires', HonoraireViewSet)
router.register(r'reglements-honoraires', ReglementHonoraireViewSet)
router.register(r'suivi-tva', SuiviTVAViewSet)
router.register(r'reclamations', ReclamationViewSet)
router.register(r'statistiques', StatistiquesViewSet, basename='statistiques')

urlpatterns = [
    # Authentification JWT
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # API REST
    path('', include(router.urls)),
    
    # Endpoints personnalisés
    path('export/excel/', include('api.export_urls')),
    path('email/', include('api.email_urls')),
]


