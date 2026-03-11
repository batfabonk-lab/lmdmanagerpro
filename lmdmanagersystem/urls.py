"""
URL configuration for lmdmanagersystem project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.http import JsonResponse


def _debug_config(request):
    """Endpoint diagnostic temporaire — À SUPPRIMER après debug."""
    key = request.GET.get('key')
    if key != 'lmddiag2026':
        return JsonResponse({'error': 'forbidden'}, status=403)
    return JsonResponse({
        'INSTITUTIONS': getattr(settings, 'INSTITUTIONS', 'NOT_SET'),
        'DATABASES_keys': list(settings.DATABASES.keys()),
        'MIDDLEWARE': settings.MIDDLEWARE,
        'DATABASE_ROUTERS': getattr(settings, 'DATABASE_ROUTERS', []),
        'DEBUG': settings.DEBUG,
        'LOGIN_URL': settings.LOGIN_URL,
        'PATH_INFO': request.META.get('PATH_INFO', '?'),
        'SCRIPT_NAME': request.META.get('SCRIPT_NAME', '?'),
    })


urlpatterns = [
    path('_diag/', _debug_config),
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('reglage/', include('reglage.urls')),
]

# Servir les fichiers media en développement
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += staticfiles_urlpatterns()
