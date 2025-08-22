from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect
from django.contrib.auth import views as auth_views
from cabinet.views import home_view
def redirect_to_login(request):
    return redirect('login')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('honoraires/', include('honoraires.urls')),
    
    
    path('api/', include('api.urls')),
    path('', home_view, name='home'), 
    path('accounts/login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('', include(('cabinet.urls', 'cabinet'), namespace='cabinet')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/', include('utilisateurs.urls')),
    path('dossiers/', include(('dossiers.urls', 'dossiers'), namespace='dossiers')),
    path('reclamations/', include(('reclamations.urls', 'reclamations'), namespace='reclamations')),
    path('juridique/', include(('juridique.urls', 'juridique'), namespace='juridique')),
    path('fiscal/', include(('fiscal.urls', 'fiscal'), namespace='fiscal')),
    path('honoraires/', include(('honoraires.urls', 'honoraires'), namespace='honoraires')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

