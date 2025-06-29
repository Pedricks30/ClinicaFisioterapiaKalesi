from django.urls import path
from .views import (
    CitaListView, 
    CitaCreateView, 
    CitaUpdateView,
    CitaDeleteView,
    citas_json,
)

app_name = 'citas'

urlpatterns = [
    path('listar/', CitaListView.as_view(), name='list'),
    path('nueva/', CitaCreateView.as_view(), name='create'),
    path('editar/<int:pk>/', CitaUpdateView.as_view(), name='update'),
    path('eliminar/<int:pk>/', CitaDeleteView.as_view(), name='delete'),
    path('api/citas/', citas_json, name='api_citas'),
]