from django.urls import path
from .views import HorarioListView, HorarioCreateView, HorarioUpdateView, HorarioDeleteView,filtrar_profesionales

urlpatterns = [
    path('listar_horario/', HorarioListView.as_view(), name='listar_horarios'),
    path('crear_horario/', HorarioCreateView.as_view(), name='crear_horario'),
    path('editar_horario/<int:pk>/', HorarioUpdateView.as_view(), name='editar_horario'),
    path('eliminar_horario/<int:pk>/', HorarioDeleteView.as_view(), name='eliminar_horario'),
    path('filtrar_profesionales/', filtrar_profesionales, name='filtrar_profesionales'),
]