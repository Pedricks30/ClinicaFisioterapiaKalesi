from django.urls import path
from .views import (
    InactivePatientListView,
    PatientListView,
    PatientCreateView,
    PatientReactivateView,
    PatientUpdateView,
    PatientDetailView,
    PatientDeleteView,
)

urlpatterns = [
    path('listar_pacientes/', PatientListView.as_view(), name='listar_pacientes'),
    path('listar_pacientes_inactivos/', InactivePatientListView.as_view(), name='listar_pacientes_inactivos'),
    path('crear_paciente/', PatientCreateView.as_view(), name='crear_paciente'),
    path('editar_paciente/<int:pk>/', PatientUpdateView.as_view(), name='editar_paciente'),
    path('eliminar/<int:pk>/', PatientDeleteView.as_view(), name='eliminar_paciente'),
    path('reactivar_paciente/<int:pk>/', PatientReactivateView.as_view(), name='reactivar_paciente'),
    path('perfil_paciente/<int:pk>/', PatientDetailView.as_view(), name='perfil_paciente'),
]