# expedientes/urls.py
from django.urls import path
from . import views


app_name = 'expedientes'

urlpatterns = [
     # Redirección del wizard principal (ES UNA FUNCIÓN, no tiene .as_view())
     path('wizard/<int:expediente_id>/', views.expediente_wizard, name='expediente_wizard'),
     
     # Detalle del expediente
     path('<int:pk>/', views.ExpedienteDetailView.as_view(), name='expediente_detail'),
     # Nuevas rutas para las secciones del expediente (SON CLASES, tienen .as_view())
     path('<int:expediente_id>/datos/', views.ExpedienteDatosView.as_view(), name='expediente_datos'),
     path('<int:expediente_id>/citas/', views.ExpedienteCitasView.as_view(), name='expediente_citas'),
     path('<int:expediente_id>/actos/', views.ExpedienteActosView.as_view(), name='expediente_actos'),
     # Evolución gráfica del paciente
     path('<int:expediente_id>/evolucion-grafica/', views.ExpedienteEvolucionGraficaView.as_view(), name='expediente_evolucion_grafica'),
     
     # Eliminar actos clínicos (AJAX)
     path('eliminar/<str:tipo>/<int:id_acto>/', views.eliminar_acto_clinico, name='eliminar_acto_clinico'),
     
     # Sesiones
     path('sesion/nueva/<int:expediente_id>/', views.crear_nueva_sesion, name='crear_nueva_sesion'),

     # ================================================================
     # NUEVAS RUTAS PARA ACTOS CLÍNICOS
     # ================================================================
     
     # Primera Consulta
     path('<int:expediente_id>/primera-consulta/crear/<int:cita_id>/', views.CrearPrimeraConsultaView.as_view(), name='crear_primera_consulta'),
     path('<int:expediente_id>/primera-consulta/editar/<int:pk>/', views.EditarPrimeraConsultaView.as_view(), name='editar_primera_consulta'),
     
     # Seguimiento
     path('<int:expediente_id>/seguimiento/crear/<int:cita_id>/', views.CrearSeguimientoView.as_view(), name='crear_seguimiento'),
     path('<int:expediente_id>/seguimiento/editar/<int:pk>/', views.EditarSeguimientoView.as_view(), name='editar_seguimiento'),
     
     # Finalización
     path('<int:expediente_id>/finalizacion/crear/<int:cita_id>/', views.CrearFinalizacionView.as_view(), name='crear_finalizacion'),
     path('<int:expediente_id>/finalizacion/editar/<int:pk>/', views.EditarFinalizacionView.as_view(), name='editar_finalizacion'),

     # Nueva vista con modelo 3D y cuestionarios
     path('<int:expediente_id>/seguimiento/cuestionarios/<int:cita_id>/', views.SeguimientoConCuestionariosView.as_view(), name='seguimiento_cuestionarios'),

     # API para cargar cuestionarios por parte del cuerpo (AJAX)
     path('api/cuestionarios-por-parte/', views.api_cuestionarios_por_parte, name='api_cuestionarios_por_parte'),
     
     # Seguimiento - Editar cuestionarios
     path('<int:expediente_id>/seguimiento/editar-cuestionarios/<int:seguimiento_id>/', views.EditarSeguimientoCuestionariosView.as_view(), name='editar_seguimiento_cuestionarios'),

     # Visualizar modelo 3D
     path('modelo-3d/', views.VisualizarModelo3DView.as_view(), name='visualizar_modelo_3d'),
     
]