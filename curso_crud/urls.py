from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login, name='login/'),
    path('forgot_password/', views.forgot_password, name='forgot_password/'),
    path('', views.index, name='curso_crud'),  # Ruta para la URL raíz
    path('registrar/', views.registrar_usuario, name='registrar_usuario/'),
]
