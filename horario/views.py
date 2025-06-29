from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from .models import Horario
from .forms import HorarioForm
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from medical.models import MedicalUser

class HorarioListView(ListView):
    model = Horario
    template_name = 'horario_asignado/horario_list.html'
    context_object_name = 'horarios'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['url_boton'] = reverse_lazy('crear_horario')
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        especialidad = self.request.GET.get('especialidad')
        profesional = self.request.GET.get('profesional')
        
        # Primero filtramos por especialidad si existe
        if especialidad:
            queryset = queryset.filter(profesional__specialties__name__icontains=especialidad)
        
        # Luego filtramos por profesional si existe
        if profesional:
            queryset = queryset.filter(profesional__name__icontains=profesional)
            
        return queryset.select_related('profesional', 'profesional__specialties')

@require_GET
def filtrar_profesionales(request):
    especialidad_id = request.GET.get('especialidad')
    
    if not especialidad_id:
        return JsonResponse({
            'error': 'Debe seleccionar una especialidad primero',
            'profesionales': []
        }, status=400)
    
    try:
        # Filtrar profesionales que tengan exactamente esta especialidad
        profesionales = MedicalUser.objects.filter(
            specialties__id=especialidad_id
        ).distinct().order_by('name')
        
        profesionales_data = [{
            'id': p.id,
            'name': p.name,
            'especialidad': p.specialties.name if p.specialties else ''
        } for p in profesionales]
        
        return JsonResponse({
            'profesionales': profesionales_data,
            'count': len(profesionales_data)
        })
    
    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'profesionales': []
        }, status=400)

class HorarioCreateView(SuccessMessageMixin, CreateView):
    model = Horario
    form_class = HorarioForm
    template_name = 'horario_asignado/horario_register.html'
    success_url = reverse_lazy('listar_horarios')
    success_message = "Horario creado exitosamente"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['especialidad_filter'] = self.request.GET.get('especialidad')
        kwargs['profesional_filter'] = self.request.GET.get('profesional')
        return kwargs

    def get_success_url(self):
        # Mantener los parámetros de filtro después de crear
        base_url = super().get_success_url()
        especialidad = self.request.GET.get('especialidad')
        profesional = self.request.GET.get('profesional')
        
        params = {}
        if especialidad:
            params['especialidad'] = especialidad
        if profesional:
            params['profesional'] = profesional
            
        if params:
            return f"{base_url}?{'&'.join([f'{k}={v}' for k, v in params.items()])}"
        return base_url

class HorarioUpdateView(SuccessMessageMixin, UpdateView):
    model = Horario
    form_class = HorarioForm
    template_name = 'horario_asignado/horario_register.html'
    success_url = reverse_lazy('listar_horarios')
    success_message = "Horario actualizado exitosamente"

    def get_success_url(self):
        # Mantener los parámetros de filtro después de editar
        base_url = super().get_success_url()
        especialidad = self.request.GET.get('especialidad')
        profesional = self.request.GET.get('profesional')
        
        params = {}
        if especialidad:
            params['especialidad'] = especialidad
        if profesional:
            params['profesional'] = profesional
            
        if params:
            return f"{base_url}?{'&'.join([f'{k}={v}' for k, v in params.items()])}"
        return base_url
    
class HorarioDeleteView(SuccessMessageMixin, DeleteView):
    model = Horario
    success_url = reverse_lazy('listar_horarios')
    success_message = "Horario eliminado exitosamente"
    # No necesitamos template_name ya que usamos modal
