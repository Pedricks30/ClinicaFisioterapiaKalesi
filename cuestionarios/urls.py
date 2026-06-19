# cuestionarios/urls.py
from django.urls import path
from . import views

app_name = 'cuestionarios'

urlpatterns = [
    # Cuestionarios CRUD
    path('', views.CuestionarioListView.as_view(), name='list'),
    path('crear/', views.CuestionarioCreateView.as_view(), name='create'),
    path('<int:pk>/', views.CuestionarioDetailView.as_view(), name='detail'),
    path('<int:pk>/editar/', views.CuestionarioUpdateView.as_view(), name='update'),
    path('<int:pk>/eliminar/', views.CuestionarioDeleteView.as_view(), name='delete'),
    
    # Preguntas CRUD
    path('<int:cuestionario_pk>/pregunta/crear/', views.PreguntaCreateView.as_view(), name='pregunta_create'),
    path('pregunta/<int:pk>/editar/', views.PreguntaUpdateView.as_view(), name='pregunta_update'),
    path('pregunta/<int:pk>/eliminar/', views.PreguntaDeleteView.as_view(), name='pregunta_delete'),

    # APIs para gestión de preguntas (desde la interfaz de expedientes)
    path('api/agregar-pregunta/', views.api_agregar_pregunta_cuestionario, name='api_agregar_pregunta'),
    path('api/editar-pregunta/', views.api_editar_pregunta_cuestionario, name='api_editar_pregunta'),
    path('api/eliminar-pregunta/', views.api_eliminar_pregunta_cuestionario, name='api_eliminar_pregunta'),
    
    # Evolución y gráficos
    path('evolucion/expediente/<int:expediente_pk>/', views.EvolucionGraficoView.as_view(), name='evolucion'),
    path('api/evolucion/<int:expediente_pk>/<int:pregunta_pk>/', views.api_evolucion_data, name='api_evolucion'),

    # Buscador de pacientes
    path('buscador/', views.BuscadorPacientesView.as_view(), name='buscador_pacientes'),
    
    # Historial de paciente
    path('historial/<int:pk>/', views.VerHistorialPacienteView.as_view(), name='historial_paciente'),
]