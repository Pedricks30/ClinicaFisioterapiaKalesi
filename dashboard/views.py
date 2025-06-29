from django.views.generic import TemplateView

class IndexView(TemplateView):
    template_name = 'inicio/index.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['mensaje'] = 'Hola, este es un mensaje desde la vista.'
        return context
