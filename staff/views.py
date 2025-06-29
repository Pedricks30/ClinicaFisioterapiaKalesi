from django.views.generic import CreateView, UpdateView, ListView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.utils.decorators import method_decorator

from staff.forms import StaffForm
from staff.models import Staff



# Crear Staff
@method_decorator(permission_required(['staff.add_staff'], raise_exception=True), name='dispatch')
class CrearStaffView(CreateView):
    model = Staff
    form_class = StaffForm
    template_name = 'staff/registration_staff.html'  # Asegúrate de tener este template
    success_url = reverse_lazy('listar_staff')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['editar'] = False  # Indica que es creación
        return context

    def form_valid(self, form):
        if 'profile_image' in self.request.FILES:
            form.instance.profile_image = self.request.FILES['profile_image']
        messages.success(self.request, 'Staff creado exitosamente.')
        return super().form_valid(form)

# Editar Staff
@method_decorator(permission_required(['staff.change_staff'], raise_exception=True), name='dispatch')
class EditarStaffView(UpdateView):
    model = Staff
    form_class = StaffForm
    template_name = 'staff/registration_staff.html'
    success_url = reverse_lazy('listar_staff')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['editar'] = True  # Indica que es creación
        return context
    
    def form_valid(self, form):
        messages.success(self.request, 'Staff editado exitosamente.')
        return super().form_valid(form)

# Listar Staff
@method_decorator(permission_required(['staff.view_staff'], raise_exception=True), name='dispatch')
class ListarStaffView(ListView):
    model = Staff
    template_name = 'staff/listar_staff.html'  # Asegúrate de tener este template
    context_object_name = 'staffs'
    ordering = ['name']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['url_boton'] = reverse_lazy('crear_staff')  # El nombre de tu URL para crear
        return context

# Eliminar Staff
@method_decorator(permission_required(['staff.delete_staff'], raise_exception=True), name='dispatch')
class EliminarStaffView(DeleteView):
    model = Staff
    success_url = reverse_lazy('listar_staff')

    def form_valid(self, form):
        email = self.get_object().email  # Obtenemos el email directamente
        response = super().form_valid(form)
        messages.success(self.request, f'El staff con email "{email}" fue eliminado correctamente.')
        return response