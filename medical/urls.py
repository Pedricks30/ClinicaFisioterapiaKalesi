from django.urls import path
from .views import (
    CrearProfesionalView, EditarProfesionalView,
    ListarProfesionalesView, EliminarProfesionalView,
    PerfilProfesionalView
)
urlpatterns = [
    # URLs para gestión de profesionales
    path('listar_profesionales/', ListarProfesionalesView.as_view(), name='listar_profesionales'),
    path('crear_profesional/', CrearProfesionalView.as_view(), name='crear_profesional'),
    path('editar_profesional/<int:pk>/', EditarProfesionalView.as_view(), name='editar_profesional'),
    path('eliminar_profesional/<int:pk>/', EliminarProfesionalView.as_view(), name='eliminar_profesional'),
    path('perfil_profesional/<int:pk>/', PerfilProfesionalView.as_view(), name='perfil_profesional'),
]