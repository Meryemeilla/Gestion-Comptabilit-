"""
Définition des routes URL et namespaces.

Fichier: config/urls.py
"""

# ==================== Imports ====================
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect
from cabinet.views import home_view
# ==================== Fonctions ====================
def redirect_to_login(request):
    return redirect('login')

urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/', include('api.urls')),
    path('', home_view, name='home'), 
    path('', include(('cabinet.urls', 'cabinet'), namespace='cabinet')),
    path('accounts/', include('utilisateurs.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('dossiers/', include(('dossiers.urls', 'dossiers'), namespace='dossiers')),
    path('reclamations/', include(('reclamations.urls', 'reclamations'), namespace='reclamations')),
    path('juridique/', include(('juridique.urls', 'juridique'), namespace='juridique')),
    path('fiscal/', include(('fiscal.urls', 'fiscal'), namespace='fiscal')),
    path('honoraires/', include(('honoraires.urls', 'honoraires'), namespace='honoraires')),
    path('comptables/', include(('comptables.urls', 'comptables'), namespace='comptables'))
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.BASE_DIR / 'static')

