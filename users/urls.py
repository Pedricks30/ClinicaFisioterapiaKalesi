from django.urls import path
from .views import (EditarDocumentTypeView, EditarEspecialidadView, EditarNivelAccesoView,
                    EliminarDocumentTypeView, EliminarEspecialidadView, EliminarNivelAccesoView,
                    GestionarDocumentTypeView, GestionarEspecialidadView, GestionarNivelAccesoView, 
                    GestionarUsuarioView, EditarUsuarioView, ListarDocumentTypesView,
                    ListarEspecialidadView, ListarNivelAccesoView, ListarUsuariosView, EliminarUsuarioView,
                    PerfilUsuarioView, CambiarContrasenaView)

urlpatterns = [
    #Users
    path('gestionar-usuario/', GestionarUsuarioView.as_view(), name='gestionar_usuario'),
    path('editar-usuario/<int:pk>/', EditarUsuarioView.as_view(), name='editar_usuario'),
    path('listar-usuarios/', ListarUsuariosView.as_view(), name='listar_usuarios'),
    path('eliminar-usuario/<int:pk>/', EliminarUsuarioView.as_view(), name='eliminar_usuario'),
    path('perfil_usuario/', PerfilUsuarioView.as_view(), name='perfil_usuario'),
    path('perfil_usuario/<int:user_id>/', PerfilUsuarioView.as_view(), name='perfil_usuario_detail'),
    path('cambiar_contrasena/', CambiarContrasenaView.as_view(), name='cambiar_contrasena'),
    #TypeDocument
    path('gestionar-documento/',GestionarDocumentTypeView.as_view(),name='gestionar_documento'),
    path('editar-documento/<int:pk>/',EditarDocumentTypeView.as_view(),name='editar_documento'),
    path('listar-documentos/',ListarDocumentTypesView.as_view(),name='listar_documentos'),
    path('eliminar-documento/<int:pk>/',EliminarDocumentTypeView.as_view(),name='eliminar_documento'),
    #Especialidades
    path('gestionar-especialidad/',GestionarEspecialidadView.as_view(),name='gestionar_especialidad'),
    path('editar-especialidad/<int:pk>/',EditarEspecialidadView.as_view(),name='editar_especialidad'),
    path('listar-especialidades/',ListarEspecialidadView.as_view(),name='listar_espacialidades'),
    path('eliminar-especialidad/<int:pk>/',EliminarEspecialidadView.as_view(),name='eliminar_especialidad'),
    #Nivel de acceso
    path('gestionar-nivel-acceso/',GestionarNivelAccesoView.as_view(),name='gestionar_nivel_acceso'),
    path('editar-nivel-acceso/<int:pk>/',EditarNivelAccesoView.as_view(),name='editar_nivel_acceso'),
    path('listar-nivel-acceso/',ListarNivelAccesoView.as_view(),name='listar_nivel_acceso'),
    path('eliminar-nivel-acceso/<int:pk>/',EliminarNivelAccesoView.as_view(),name='eliminar_nivel_acceso'),
]