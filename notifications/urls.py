from django.urls import path
from .views import ver_notificaciones, marcar_como_leida

app_name = 'notifications'

urlpatterns = [
    path('', ver_notificaciones, name='ver_notificaciones'),
    path('<int:pk>/leida/', marcar_como_leida, name='marcar_como_leida'),
]