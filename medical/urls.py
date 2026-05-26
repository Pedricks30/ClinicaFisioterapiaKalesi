from django.urls import path
from .views import (
    CrearMedicoView,
    EditarMedicoView,
    ListarMedicoView,
    EliminarMedicoView,
    PerfilMedicoView,
)
from .api_views import buscar_medicos

urlpatterns = [
    path('crear/', CrearMedicoView.as_view(), name='crear_profesional'),
    path('editar/<int:pk>/', EditarMedicoView.as_view(), name='editar_profesional'),
    path('listar/', ListarMedicoView.as_view(), name='listar_profesionales'),
    path('eliminar/<int:pk>/', EliminarMedicoView.as_view(), name='eliminar_profesional'),
    path('perfil/<int:pk>/', PerfilMedicoView.as_view(), name='perfil_profesional'),
    # API para búsqueda AJAX
    path('api/buscar-medicos/', buscar_medicos, name='api_buscar_medicos'),
]