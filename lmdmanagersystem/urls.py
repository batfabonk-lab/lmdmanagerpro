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
from django.urls import path, include, re_path
from django.conf import settings
from django.views.static import serve
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from lmdmanagersystem.setup_view import run_setup

urlpatterns = [
    path('setup-migrate/', run_setup, name='setup_migrate'),
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('reglage/', include('reglage.urls')),
]

# Servir static + media en production (cPanel/Passenger, pas de serveur séparé)
# static() de Django ne fonctionne PAS quand DEBUG=False, donc on utilise re_path + serve
urlpatterns += [
    re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]
if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
