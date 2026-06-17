# citas/urls.py
from django.urls import path
from .views import (
    CitasCalendarioView,
    CitaCreateAjaxView,
    CitaUpdateAjaxView,
    CitaDeleteAjaxView,
    CitasBusquedaView,
    CitaDetailView,
    CitaConfirmarAjaxView,
    CitaIniciarAjaxView,
    CitaCompletarAjaxView,
)
from .api_views import (
    calcular_tipo_cita,
    filtrar_profesionales_por_especialidad,
    get_horarios_profesional,
    get_horas_disponibles,
    get_eventos_calendario,
    buscar_citas,
    verificar_estado_paciente,
    verificar_puede_finalizar,
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
    
    # Acciones AJAX adicionales
    path('api/confirmar/<int:pk>/', CitaConfirmarAjaxView.as_view(), name='api_confirmar'),
    path('api/iniciar/<int:pk>/', CitaIniciarAjaxView.as_view(), name='api_iniciar'),
    path('api/completar/<int:pk>/', CitaCompletarAjaxView.as_view(), name='api_completar'),
    
    # Endpoints API
    path('api/filtrar-profesionales/', filtrar_profesionales_por_especialidad, name='api_filtrar_profesionales'),
    path('api/horarios-profesional/<int:profesional_id>/', get_horarios_profesional, name='api_horarios_profesional'),
    path('api/horas-disponibles/<int:profesional_id>/<str:fecha_str>/', get_horas_disponibles, name='api_horas_disponibles'),
    path('api/eventos/', get_eventos_calendario, name='api_eventos'),
    path('api/buscar-citas/', buscar_citas, name='api_buscar_citas'),
    path('api/verificar-finalizacion/', verificar_puede_finalizar, name='api_verificar_finalizacion'),
    path('api/verificar-estado-paciente/', verificar_estado_paciente, name='api_verificar_estado_paciente'),
    path('api/calcular-tipo-cita/', calcular_tipo_cita, name='api_calcular_tipo_cita'),
]