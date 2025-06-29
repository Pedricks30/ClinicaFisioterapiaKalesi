from django.urls import path
from .views import (
    CrearStaffView,
    EditarStaffView,
    ListarStaffView,
    EliminarStaffView,
)

urlpatterns = [
    path('crear/', CrearStaffView.as_view(), name='crear_staff'),
    path('editar/<int:pk>/', EditarStaffView.as_view(), name='editar_staff'),
    path('eliminar/<int:pk>/', EliminarStaffView.as_view(), name='eliminar_staff'),
    path('listar/', ListarStaffView.as_view(), name='listar_staff'),
]
