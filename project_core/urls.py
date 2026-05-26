"""
URL configuration for project_core project.

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

urlpatterns = [
    path('', include('authentication.urls')),  # Redirige la URL raíz a la app de autenticación
    path('admin/', admin.site.urls),
    path('users/', include('users.urls')),  # URLs de usuarios
    path('physiotherapist/', include('physiotherapist.urls')),
    path('dashboard/', include('dashboard.urls')),  # URLs del dashboard
    path('medical/', include('medical.urls')),  # URLs de la app médica
    path('horario/', include('horario.urls')),  # URLs de la app médica
    path('citas/', include('citas.urls')),  # URLs de la app de citas
    path('paciente/', include('paciente.urls')),  # URLs de la app de pacientes}
    #path('expedientes/', include('expedientes.urls')),  # URLs de la app de expediente
    path('notifications/', include('notifications.urls')),  # URLs de notificaciones
    
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)