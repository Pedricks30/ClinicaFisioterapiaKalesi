from django.urls import path
from django.contrib.auth import views as auth_views
from .views import CustomLoginView
from django.views.generic.base import RedirectView

urlpatterns = [
    path('', RedirectView.as_view(url='/login/')),  # Redirige la ruta raíz a /login/
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('reset_password/', auth_views.PasswordResetView.as_view(template_name="auth/password_reset.html"), name='password_reset'),
    path('reset_password_send/', auth_views.PasswordResetDoneView.as_view(template_name="auth/password_reset_done.html"), name='password_reset_done'),
    path('reset/<uidb64>/<token>', auth_views.PasswordResetConfirmView.as_view(template_name="auth/password_reset_confirm.html"), name='password_reset_confirm'),
    path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(template_name="auth/password_reset_complete.html"), name='password_reset_complete'),
]