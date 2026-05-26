from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView, View
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from users.models import Specialties
from .models import Cita, CitaHistorico
from .forms import CitaModalForm, BusquedaCitaForm


# =============================================================================
# VISTA PRINCIPAL: CALENDARIO DE CITAS
# =============================================================================
class CitasCalendarioView(LoginRequiredMixin, View):
    """
    Página principal con:
    - Filtro de especialidad → profesional
    - Tabla de horarios del profesional
    - FullCalendar con citas
    - Modal para crear/editar citas
    """
    template_name = 'citas/citas_calendario.html'
    
    def get(self, request, *args, **kwargs):
        context = {
            'especialidades': Specialties.objects.all().order_by('specialties'),
            'form': CitaModalForm(),
        }
        return render(request, self.template_name, context)


# =============================================================================
# CREAR CITA (DESDE EL MODAL - AJAX)
# =============================================================================
class CitaCreateAjaxView(LoginRequiredMixin, View):
    """
    Crea una cita desde el modal del calendario vía AJAX.
    """
    def post(self, request, *args, **kwargs):
        profesional_id = request.POST.get('profesional_id')
        if not profesional_id:
            return JsonResponse({'success': False, 'error': 'Profesional no especificado'}, status=400)
        
        from users.models import CustomUser
        profesional = get_object_or_404(CustomUser, pk=profesional_id)
        
        form = CitaModalForm(
            request.POST,
            profesional=profesional,
            creada_por=request.user
        )
        
        if form.is_valid():
            cita = form.save()
            return JsonResponse({
                'success': True,
                'message': 'Cita creada exitosamente',
                'cita_id': cita.id
            })
        
        return JsonResponse({'success': False, 'errors': form.errors}, status=400)


# =============================================================================
# EDITAR CITA (DESDE EL MODAL - AJAX)
# =============================================================================
class CitaUpdateAjaxView(LoginRequiredMixin, View):
    """
    Actualiza una cita desde el modal del calendario vía AJAX.
    """
    def post(self, request, pk, *args, **kwargs):
        cita = get_object_or_404(Cita, pk=pk)
        form = CitaModalForm(
            request.POST,
            instance=cita,
            profesional=cita.profesional,
            creada_por=request.user
        )
        
        if form.is_valid():
            cita = form.save()
            return JsonResponse({
                'success': True,
                'message': 'Cita actualizada exitosamente',
                'cita_id': cita.id
            })
        
        return JsonResponse({'success': False, 'errors': form.errors}, status=400)


# =============================================================================
# ELIMINAR CITA (AJAX)
# =============================================================================
class CitaDeleteAjaxView(LoginRequiredMixin, View):
    """
    Elimina/cancela una cita vía AJAX.
    """
    def post(self, request, pk, *args, **kwargs):
        cita = get_object_or_404(Cita, pk=pk)
        
        if not cita.puede_ser_cancelada:
            return JsonResponse({
                'success': False,
                'error': 'La cita no puede ser cancelada. Mínimo 24 horas de anticipación.'
            }, status=400)
        
        cita.cancelar(request.user)
        return JsonResponse({'success': True, 'message': 'Cita cancelada exitosamente'})


# =============================================================================
# BÚSQUEDA GENERAL DE CITAS
# =============================================================================
class CitasBusquedaView(LoginRequiredMixin, ListView):
    """
    Página de búsqueda general de citas con tabla de resultados.
    """
    model = Cita
    template_name = 'citas/citas_busqueda.html'
    context_object_name = 'citas'
    paginate_by = 15
    
    def get_queryset(self):
        queryset = super().get_queryset().select_related('paciente', 'profesional')
        
        # Filtros según tipo de usuario
        user = self.request.user
        if user.is_medico or user.is_fisio:
            queryset = queryset.filter(profesional=user)
        
        # Filtros del formulario
        q = self.request.GET.get('q', '')
        estado = self.request.GET.get('estado', '')
        fecha_desde = self.request.GET.get('fecha_desde', '')
        fecha_hasta = self.request.GET.get('fecha_hasta', '')
        
        if q:
            from django.db.models import Q
            queryset = queryset.filter(
                Q(paciente__nombres__icontains=q) |
                Q(paciente__apellidos__icontains=q) |
                Q(paciente__documento_identidad__icontains=q) |
                Q(profesional__first_name__icontains=q) |
                Q(profesional__last_name__icontains=q) |
                Q(motivo__icontains=q)
            )
        
        if estado:
            queryset = queryset.filter(estado=estado)
        
        if fecha_desde:
            queryset = queryset.filter(fecha__date__gte=fecha_desde)
        if fecha_hasta:
            queryset = queryset.filter(fecha__date__lte=fecha_hasta)
        
        return queryset.order_by('-fecha')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = BusquedaCitaForm(self.request.GET or None)
        context['estados'] = dict(Cita.ESTADO_CHOICES)
        return context


# =============================================================================
# DETALLE DE CITA
# =============================================================================
class CitaDetailView(LoginRequiredMixin, DetailView):
    model = Cita
    template_name = 'citas/cita_detail.html'
    context_object_name = 'cita'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['historico'] = self.object.historico.all().order_by('-created_at')[:10]
        return context