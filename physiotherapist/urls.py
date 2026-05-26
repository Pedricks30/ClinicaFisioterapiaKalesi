from django.urls import path

from physiotherapist.api_views import buscar_fisioterapeutas
from .views import (
    CrearFisioterapeutaView,
    EditarFisioterapeutaView,
    ListarFisioterapeutaView,
    EliminarFisioterapeutaView,
    PerfilFisioterapeutaView
)

urlpatterns = [
    path('listar_fisioterapeutas/', ListarFisioterapeutaView.as_view(), name='listar_fisioterapeuta'),
    path('crear_fisioterapeuta/', CrearFisioterapeutaView.as_view(), name='crear_fisioterapeuta'),
    path('editar_fisioterapeuta/<int:pk>/', EditarFisioterapeutaView.as_view(), name='editar_fisioterapeuta'),
    path('eliminar_fisioterapeuta/<int:pk>/', EliminarFisioterapeutaView.as_view(), name='eliminar_fisioterapeuta'),
    path('perfil_fisioterapeuta/<int:pk>/', PerfilFisioterapeutaView.as_view(), name='perfil_fisioterapeuta'),
    path('api/buscar-fisioterapeutas/', buscar_fisioterapeutas, name='api_buscar_fisioterapeutas'),
]