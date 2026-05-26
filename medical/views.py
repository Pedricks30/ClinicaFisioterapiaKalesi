from django.urls import reverse_lazy
from django.contrib.auth.decorators import permission_required, login_required
from django.utils.decorators import method_decorator
from django.views.generic import (
    CreateView, UpdateView, DeleteView, ListView, DetailView
)
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from .models import Medico
from .forms import MedicoForm


# -------------------------------------------------------------------------
# CREAR PERFIL DE MÉDICO
# -------------------------------------------------------------------------
@method_decorator(permission_required(['medical.add_medico'], raise_exception=True), name='dispatch')
class CrearMedicoView(SuccessMessageMixin, CreateView):
    """
    Vista para crear un perfil de médico para un usuario MEDIC existente.
    Se selecciona el usuario mediante un buscador/selector en el formulario.
    """
    model = Medico
    form_class = MedicoForm
    template_name = 'medical/register_medical.html'
    success_url = reverse_lazy('listar_profesionales')
    success_message = "Perfil médico creado exitosamente."

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['editar'] = False
        return context


# -------------------------------------------------------------------------
# EDITAR PERFIL DE MÉDICO
# -------------------------------------------------------------------------
@method_decorator(permission_required(['medical.change_medico'], raise_exception=True), name='dispatch')
class EditarMedicoView(SuccessMessageMixin, UpdateView):
    """
    Vista para editar el perfil de un médico existente.
    El campo 'user' está deshabilitado en edición.
    """
    model = Medico
    form_class = MedicoForm
    template_name = 'medical/register_medical.html'
    success_url = reverse_lazy('listar_profesionales')
    success_message = "Perfil médico actualizado exitosamente."
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['editar'] = True
        return context


# -------------------------------------------------------------------------
# LISTAR MÉDICOS
# -------------------------------------------------------------------------
@method_decorator(login_required, name='dispatch')
class ListarMedicoView(ListView):
    """
    Vista para listar todos los médicos registrados.
    """
    model = Medico
    template_name = 'medical/list_medical.html'
    context_object_name = 'profesionales'
    ordering = ['user__last_name', 'user__first_name']
    

    def get_queryset(self):
        """Optimiza la consulta con select_related y prefetch_related"""
        return super().get_queryset().select_related(
            'user', 'user__document_type', 'specialties'
        ).prefetch_related(
            'especialidades_secundarias'
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['url_boton'] = reverse_lazy('crear_profesional')
        return context


# -------------------------------------------------------------------------
# ELIMINAR MÉDICO
# -------------------------------------------------------------------------
@method_decorator(permission_required(['medical.delete_medico'], raise_exception=True), name='dispatch')
class EliminarMedicoView(SuccessMessageMixin, DeleteView):
    """
    Vista para eliminar un perfil médico.
    """
    model = Medico
    success_url = reverse_lazy('listar_profesionales')
    
    def delete(self, request, *args, **kwargs):
        medico = self.get_object()
        nombre = medico.user.get_full_name()
        messages.success(request, f'El perfil médico de "{nombre}" fue eliminado correctamente.')
        return super().delete(request, *args, **kwargs)


# -------------------------------------------------------------------------
# PERFIL DETALLADO DE MÉDICO
# -------------------------------------------------------------------------
@method_decorator(login_required, name='dispatch')
class PerfilMedicoView(DetailView):
    """
    Vista para ver el perfil detallado de un médico.
    """
    model = Medico
    template_name = 'medical/profile_medical.html'
    context_object_name = 'medico'
    
    def get_queryset(self):
        """Optimiza la consulta con select_related"""
        return super().get_queryset().select_related(
            'user', 'user__document_type', 'specialties'
        ).prefetch_related('especialidades_secundarias')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['usuario'] = self.object.user
        return context