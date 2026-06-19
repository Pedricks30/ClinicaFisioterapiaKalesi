from django.urls import path
from .views import busqueda_rapida, dashboard, api_notificaciones_citas, api_notificaciones_alertas

urlpatterns = [
    path('', dashboard, name='dashboard'),
    path('api/notificaciones/citas/', api_notificaciones_citas, name='api_notificaciones_citas'),
    path('api/notificaciones/alertas/', api_notificaciones_alertas, name='api_notificaciones_alertas'),
    path('api/busqueda-rapida/', busqueda_rapida, name='busqueda_rapida'),
]