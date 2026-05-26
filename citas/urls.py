from django.urls import path
from .views import (
    CitasCalendarioView,
    CitaCreateAjaxView,
    CitaUpdateAjaxView,
    CitaDeleteAjaxView,
    CitasBusquedaView,
    CitaDetailView,
)
from .api_views import (
    filtrar_profesionales_por_especialidad,
    get_horarios_profesional,
    get_horas_disponibles,
    get_eventos_calendario,
    buscar_citas,
)

app_name = 'citas'

urlpatterns = [
    # Páginas principales
    path('calendario/', CitasCalendarioView.as_view(), name='calendario'),
    path('busqueda/', CitasBusquedaView.as_view(), name='busqueda'),
    path('detalle/<int:pk>/', CitaDetailView.as_view(), name='detail'),
    
    # Acciones AJAX
    path('api/crear/', CitaCreateAjaxView.as_view(), name='api_create'),
    path('api/editar/<int:pk>/', CitaUpdateAjaxView.as_view(), name='api_update'),
    path('api/eliminar/<int:pk>/', CitaDeleteAjaxView.as_view(), name='api_delete'),
    
    # Endpoints API
    path('api/filtrar-profesionales/', filtrar_profesionales_por_especialidad, name='api_filtrar_profesionales'),
    path('api/horarios-profesional/<int:profesional_id>/', get_horarios_profesional, name='api_horarios_profesional'),
    path('api/horas-disponibles/<int:profesional_id>/<str:fecha_str>/', get_horas_disponibles, name='api_horas_disponibles'),
    path('api/eventos/', get_eventos_calendario, name='api_eventos'),
    path('api/buscar-citas/', buscar_citas, name='api_buscar_citas'),
]