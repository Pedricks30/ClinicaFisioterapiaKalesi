from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView
from authentication.forms import CustomAuthenticationForm

@method_decorator(never_cache, name='dispatch')
class CustomLoginView(LoginView):
    template_name = 'auth/login.html'
    form_class = CustomAuthenticationForm
    redirect_authenticated_user = True

    def get_success_url(self):
        # Redirige a 'dashboard' o a la URL en el parámetro 'next'
        return self.request.GET.get('next', reverse_lazy('dashboard'))