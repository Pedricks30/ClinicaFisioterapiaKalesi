from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from notifications.models import Notificacion
from django.urls import reverse_lazy
from .models import Cita
from .forms import CitaForm
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from citas.models import Cita
import json

class CitaListView(ListView):
    model = Cita
    template_name = 'citas/cita_list.html'
    context_object_name = 'citas'

    def get_queryset(self):
        queryset = Cita.objects.all().select_related('paciente', 'profesional')
        
        # Si es un médico, filtrar solo sus citas
        if hasattr(self.request.user, 'medical_user'):
            return queryset.filter(profesional=self.request.user.medical_user)
        
        # Si es admin o staff, mostrar todas
        elif self.request.user.is_staff:
            return queryset
            
        # Para otros usuarios (como pacientes)
        elif hasattr(self.request.user, 'patient'):
            return queryset.filter(paciente=self.request.user.patient)
            
        return Cita.objects.none()

class CitaCreateView(CreateView):
    model = Cita
    form_class = CitaForm
    template_name = 'citas/cita_form.html'
    success_url = reverse_lazy('citas:list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['notificaciones'] = Notificacion.objects.filter(
            usuario=self.request.user, leida=False
        ).order_by('-fecha')
        return context

    def form_valid(self, form):
        form.instance.profesional = self.request.user
        return super().form_valid(form)

class CitaUpdateView(UpdateView):
    model = Cita
    form_class = CitaForm
    template_name = 'citas/cita_form.html'
    success_url = reverse_lazy('citas:list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['notificaciones'] = Notificacion.objects.filter(
            usuario=self.request.user, leida=False
        ).order_by('-fecha')
        return context

@require_GET
def citas_json(request):
    citas = Cita.objects.filter(
        profesional=request.user  # o el filtro que necesites
    ).select_related('paciente', 'profesional')
    
    events = []
    for cita in citas:
        events.append({
            'id': cita.id,
            'title': f"{cita.paciente.name} - {cita.motivo[:20]}...",
            'start': f"{cita.fecha}T{cita.hora_inicio}",
            'end': f"{cita.fecha}T{cita.hora_fin}",
            'color': self.get_color_estado(cita.estado),
            'extendedProps': {
                'paciente': cita.paciente.name,
                'profesional': cita.profesional.name,
                'motivo': cita.motivo,
                'estado': cita.get_estado_display()
            }
        })
    
    return JsonResponse(events, safe=False)

def get_color_estado(self, estado):
    colores = {
        'P': '#ffc107',  # Amarillo (pendiente)
        'C': '#28a745',  # Verde (confirmada)
        'A': '#17a2b8',  # Azul (atendida)
        'N': '#dc3545'   # Rojo (cancelada)
    }
    return colores.get(estado, '#6c757d')

class CitaDetailView(ListView):
    model = Cita
    template_name = 'citas/cita_detail.html'
    context_object_name = 'cita'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['notificaciones'] = Notificacion.objects.filter(
            usuario=self.request.user, leida=False
        ).order_by('-fecha')
        return context
    
class CitaDeleteView(DeleteView):
    model = Cita
    template_name = 'citas/cita_confirm_delete.html'
    success_url = reverse_lazy('citas:list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['notificaciones'] = Notificacion.objects.filter(
            usuario=self.request.user, leida=False
        ).order_by('-fecha')
        return context