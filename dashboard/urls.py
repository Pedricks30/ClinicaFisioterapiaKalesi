from django.urls import path
from .views import IndexView

urlpatterns = [
    path('', IndexView.as_view(), name='dashboard'),  # Ruta para la URL raíz
]