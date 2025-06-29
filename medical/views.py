from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.contrib.auth.decorators import permission_required, login_required
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.views.generic import (
    CreateView, UpdateView, DeleteView, ListView, DetailView
)
from .models import MedicalUser, DocumentType, Specialties
from .forms import MedicalUserForm

# Vistas para MedicalUser
@method_decorator(permission_required(['medical.add_medicaluser'], raise_exception=True), name='dispatch')
class CrearProfesionalView(CreateView):
    model = MedicalUser
    form_class = MedicalUserForm
    template_name = 'medical/register_medical.html'
    success_url = reverse_lazy('listar_profesionales')

    def form_valid(self, form):
        messages.success(self.request, 'Profesional agregado exitosamente.')
        return super().form_valid(form)

@method_decorator(permission_required(['medical.change_medicaluser'], raise_exception=True), name='dispatch')
class EditarProfesionalView(UpdateView):
    model = MedicalUser
    form_class = MedicalUserForm
    template_name = 'medical/register_medical.html'
    success_url = reverse_lazy('listar_profesionales')

    def form_valid(self, form):
        messages.success(self.request, 'Profesional actualizado exitosamente.')
        return super().form_valid(form)

class ListarProfesionalesView(ListView):
    model = MedicalUser
    template_name = 'medical/list_medical.html'
    context_object_name = 'profesionales'
    ordering = ['name']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['url_boton'] = reverse_lazy('crear_profesional')
        return context

@method_decorator(permission_required(['medical.delete_medicaluser'], raise_exception=True), name='dispatch')
class EliminarProfesionalView(DeleteView):
    model = MedicalUser
    success_url = reverse_lazy('listar_profesionales')

    def form_valid(self, form):
        name = self.get_object().name
        response = super().form_valid(form)
        messages.success(self.request, f'El profesional "{name}" ha sido eliminado exitosamente.')
        return response

@method_decorator(login_required, name='dispatch')
class PerfilProfesionalView(DetailView):
    model = MedicalUser
    template_name = 'medical/profile_medical.html'
    context_object_name = 'profesional'
    pk_url_kwarg = 'pk'  # Esto es opcional ya que es el valor por defecto

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Agrega aquí cualquier contexto adicional que necesites
        return context