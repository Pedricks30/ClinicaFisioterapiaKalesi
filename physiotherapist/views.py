from django.views.generic import CreateView, UpdateView, ListView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.contrib.auth.decorators import permission_required, login_required
from django.utils.decorators import method_decorator
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.shortcuts import redirect
from .forms import FisioterapeutaForm
from .models import Fisioterapeuta
# -------------------------------------------------------------------------
# CREAR PERFIL DE FISIOTERAPEUTA
# -------------------------------------------------------------------------
@method_decorator(permission_required(['physiotherapist.add_fisioterapeuta'], raise_exception=True), name='dispatch')
class CrearFisioterapeutaView(SuccessMessageMixin, CreateView):
    """
    Vista para crear un perfil de fisioterapeuta para un usuario FISIO existente.
    Se selecciona el usuario mediante un buscador/selector en el formulario.
    """
    model = Fisioterapeuta
    form_class = FisioterapeutaForm
    template_name = 'physiotherapist/registration_fisioterapeuta.html'
    success_url = reverse_lazy('listar_fisioterapeuta')
    success_message = "Perfil de fisioterapeuta creado exitosamente."

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['editar'] = False
        return context


# -------------------------------------------------------------------------
# EDITAR PERFIL DE FISIOTERAPEUTA
# -------------------------------------------------------------------------
@method_decorator(permission_required(['physiotherapist.change_fisioterapeuta'], raise_exception=True), name='dispatch')
class EditarFisioterapeutaView(SuccessMessageMixin, UpdateView):
    """
    Vista para editar el perfil de un fisioterapeuta existente.
    """
    model = Fisioterapeuta
    form_class = FisioterapeutaForm
    template_name = 'physiotherapist/registration_fisioterapeuta.html'
    success_url = reverse_lazy('listar_fisioterapeuta')
    success_message = "Perfil de fisioterapeuta actualizado exitosamente."

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['editar'] = True
        return context


# -------------------------------------------------------------------------
# LISTAR FISIOTERAPEUTAS
# -------------------------------------------------------------------------
@method_decorator(permission_required(['physiotherapist.view_fisioterapeuta'], raise_exception=True), name='dispatch')
class ListarFisioterapeutaView(ListView):
    """
    Vista para listar todos los fisioterapeutas registrados.
    """
    model = Fisioterapeuta
    template_name = 'physiotherapist/listar_fisioterapeuta.html'
    context_object_name = 'fisioterapeutas'  # Corregido: nombre en minúscula para consistencia
    ordering = ['user__last_name', 'user__first_name']

    def get_queryset(self):
        """Optimiza la consulta con select_related"""
        return super().get_queryset().select_related('user', 'user__document_type', 'specialties')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['url_boton'] = reverse_lazy('crear_fisioterapeuta')
        return context


# -------------------------------------------------------------------------
# ELIMINAR FISIOTERAPEUTA
# -------------------------------------------------------------------------
@method_decorator(permission_required(['physiotherapist.delete_fisioterapeuta'], raise_exception=True), name='dispatch')
class EliminarFisioterapeutaView(SuccessMessageMixin, DeleteView):
    """
    Vista para eliminar un perfil de fisioterapeuta.
    """
    model = Fisioterapeuta
    success_url = reverse_lazy('listar_fisioterapeuta')

    def delete(self, request, *args, **kwargs):
        fisioterapeuta = self.get_object()
        nombre = fisioterapeuta.user.get_full_name()
        messages.success(request, f'El perfil de fisioterapeuta de "{nombre}" fue eliminado correctamente.')
        return super().delete(request, *args, **kwargs)


# -------------------------------------------------------------------------
# PERFIL DETALLADO DE FISIOTERAPEUTA
# -------------------------------------------------------------------------
@method_decorator(login_required, name='dispatch')
class PerfilFisioterapeutaView(DetailView):
    """
    Vista para ver el perfil detallado de un fisioterapeuta.
    """
    model = Fisioterapeuta
    template_name = 'physiotherapist/profile_fisioterapeuta.html'
    context_object_name = 'fisioterapeuta'
    
    def get_queryset(self):
        """Optimiza la consulta con select_related"""
        return super().get_queryset().select_related('user', 'user__document_type', 'specialties')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['usuario'] = self.object.user
        return context