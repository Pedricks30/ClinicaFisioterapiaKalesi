from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin
from django.views.decorators.http import require_GET
from .models import Horario
from .forms import HorarioForm

# -------------------------------------------------------------------------
# VISTAS BASADAS EN CLASE
# -------------------------------------------------------------------------
class HorarioListView(ListView):
    model = Horario
    template_name = 'horario_asignado/horario_list.html'
    context_object_name = 'horarios'
    paginate_by = 10

    def get_queryset(self):
        return super().get_queryset().select_related(
            'profesional',
            'profesional__perfil_medico__specialties',
            'profesional__perfil_fisioterapeuta__specialties',
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['url_boton'] = reverse_lazy('crear_horario')
        return context


class HorarioCreateView(SuccessMessageMixin, CreateView):
    model = Horario
    form_class = HorarioForm
    template_name = 'horario_asignado/horario_register.html'
    success_url = reverse_lazy('listar_horarios')
    success_message = "Horario creado exitosamente."


class HorarioUpdateView(SuccessMessageMixin, UpdateView):
    model = Horario
    form_class = HorarioForm
    template_name = 'horario_asignado/horario_register.html'
    success_url = reverse_lazy('listar_horarios')
    success_message = "Horario actualizado exitosamente."

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['editar'] = True
        return context


class HorarioDeleteView(SuccessMessageMixin, DeleteView):
    model = Horario
    success_url = reverse_lazy('listar_horarios')
    success_message = "Horario eliminado exitosamente."