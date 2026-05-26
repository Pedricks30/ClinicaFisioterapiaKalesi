from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import permission_required
from django.utils.decorators import method_decorator
from django.http import HttpResponseRedirect, JsonResponse
from django.db.models import Q
from .models import Patient
from .forms import PatientForm
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages

@method_decorator(permission_required(['paciente.view_patient'], raise_exception=True), name='dispatch')
class PatientListView(ListView):
    model = Patient
    template_name = 'patient/list_paciente.html'
    context_object_name = 'pacientes'
    paginate_by = 15

    def get_queryset(self):
        # Filtra solo pacientes activos
        queryset = super().get_queryset().filter(estado=True)
        search_query = self.request.GET.get('search', '')
        
        if search_query:
            queryset = queryset.filter(
                Q(nombres__icontains=search_query) |
                Q(apellidos__icontains=search_query) |
                Q(documento_identidad__icontains=search_query) |
                Q(email__icontains=search_query) |
                Q(numero_telefono__icontains=search_query)
            )
        
        return queryset.select_related('tipo_documento', 'creado_por')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['url_boton'] = reverse_lazy('crear_paciente')
        context['search'] = self.request.GET.get('search', '')
        return context

@method_decorator(permission_required(['paciente.view_patient'], raise_exception=True), name='dispatch')
class InactivePatientListView(ListView):
    model = Patient
    template_name = 'patient/list_paciente_inactive.html'
    context_object_name = 'pacientes'
    paginate_by = 15

    def get_queryset(self):
        queryset = super().get_queryset().filter(estado=False)
        search_query = self.request.GET.get('search', '')
        
        if search_query:
            queryset = queryset.filter(
                Q(nombres__icontains=search_query) |
                Q(apellidos__icontains=search_query) |
                Q(documento_identidad__icontains=search_query) |
                Q(email__icontains=search_query) |
                Q(numero_telefono__icontains=search_query)
            )
        
        return queryset.select_related('tipo_documento', 'creado_por')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['is_inactive_list'] = True
        return context

@method_decorator(permission_required(['paciente.change_patient'], raise_exception=True), name='dispatch')
class PatientReactivateView(View):
    def post(self, request, pk):
        paciente = get_object_or_404(Patient, pk=pk)
        paciente.estado = True
        paciente.save()
        messages.success(request, 'Paciente reactivado exitosamente.')
        return redirect('listar_pacientes_inactivos')
    
@method_decorator(permission_required(['paciente.add_patient'], raise_exception=True), name='dispatch')
class PatientCreateView(SuccessMessageMixin, CreateView):
    model = Patient
    form_class = PatientForm
    template_name = 'patient/registration_paciente.html'
    success_url = reverse_lazy('listar_pacientes')
    success_message = "Paciente creado exitosamente."
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['editar'] = False
        return context
    
@method_decorator(permission_required(['paciente.change_patient'], raise_exception=True), name='dispatch')
class PatientUpdateView(SuccessMessageMixin, UpdateView):
    model = Patient
    form_class = PatientForm
    template_name = 'patient/registration_paciente.html'
    success_url = reverse_lazy('listar_pacientes')
    success_message = "Paciente actualizado exitosamente."
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['editar'] = True
        return context

@method_decorator(permission_required(['paciente.view_patient'], raise_exception=True), name='dispatch')
class PatientDetailView(DetailView):
    model = Patient
    template_name = 'patient/profile_paciente.html'
    context_object_name = 'paciente'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        paciente = self.object
        context['edad'] = paciente.edad
        context['es_menor'] = paciente.es_menor
        context['contacto_emergencia'] = paciente.contacto_emergencia
        return context

@method_decorator(permission_required(['paciente.delete_patient'], raise_exception=True), name='dispatch')
class PatientDeleteView(SuccessMessageMixin, DeleteView):
    model = Patient
    success_url = reverse_lazy('listar_pacientes')
    success_message = 'Paciente desactivado exitosamente.'
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        
        # Verificar si el paciente tiene citas programadas
        if hasattr(self.object, 'cita_set') and self.object.cita_set.filter(estado__in=['PENDIENTE', 'CONFIRMADA']).exists():
            messages.error(request, 'No se puede desactivar el paciente porque tiene citas programadas.')
            return redirect('listar_pacientes')
        
        # Eliminación lógica (cambiar estado a False)
        self.object.estado = False
        self.object.save()
        
        messages.success(request, self.success_message)
        return HttpResponseRedirect(self.get_success_url())