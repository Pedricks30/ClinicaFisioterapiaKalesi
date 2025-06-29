from django.http import JsonResponse
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import permission_required, login_required
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.shortcuts import get_object_or_404, render
from django.views import View
from django.views.generic import (
    CreateView, UpdateView, DeleteView, ListView, DetailView
)
from .models import AccessLevel, CustomUser, DocumentType, Specialties
from .forms import AccessLevelForm, CustomUserCreationForm, CustomPasswordChangeForm, DocumentTypeForm, SpecialtiesForm
from django.contrib.auth.views import PasswordChangeView

User = get_user_model()

@method_decorator(permission_required(['user.add_customuser', 'user.change_customuser'], raise_exception=True), name='dispatch')
class GestionarUsuarioView(CreateView):
    model = CustomUser
    form_class = CustomUserCreationForm
    template_name = 'user/registration_user.html'
    success_url = reverse_lazy('listar_usuarios')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['editar'] = False
        return context
    
    def form_valid(self, form):
        messages.success(self.request, 'Usuario agregado exitosamente.')
        return super().form_valid(form)

class EditarUsuarioView(UpdateView):
    model = CustomUser
    form_class = CustomUserCreationForm
    template_name = 'user/registration_user.html'
    success_url = reverse_lazy('listar_usuarios')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['editar'] = True
        return context
    
    def form_valid(self, form):
        messages.success(self.request, 'Usuario editado exitosamente.')
        return super().form_valid(form)

class ListarUsuariosView(ListView):
    model = CustomUser
    template_name = 'user/list_users.html'
    context_object_name = 'usuarios'
    ordering = ['username']

    def get_context_data(self, **kwargs):
        # Llama al método get_context_data de la clase padre
        context = super().get_context_data(**kwargs)
        # Agrega la URL del botón "Crear" al contexto
        context['url_boton'] = reverse('gestionar_usuario')  # Cambia 'gestionar_usuario' por el nombre de tu URL
        return context

@method_decorator(permission_required('user.delete_customuser', raise_exception=True), name='dispatch')
class EliminarUsuarioView(DeleteView):
    model = CustomUser
    success_url = reverse_lazy('listar_usuarios')

    def form_valid(self, form):
        username = self.get_object().username
        response = super().form_valid(form)
        messages.success(self.request, f'El usuario "{username}" ha sido eliminado exitosamente.')
        return response

@method_decorator(login_required, name='dispatch')
class PerfilUsuarioView(DetailView):
    model = User
    template_name = 'user/profile_user.html'
    context_object_name = 'user'

    def get_object(self, queryset=None):
        # Si se proporciona un user_id, obtener ese usuario
        if 'user_id' in self.kwargs:
            return get_object_or_404(User, id=self.kwargs['user_id'])
        # Si no, devolver el usuario actual
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Determinar si la vista se está usando para ver el perfil de otro usuario
        context['is_from_list'] = 'user_id' in self.kwargs
        return context

@method_decorator(permission_required(['user.add_documenttype', 'user.change_documenttype'], raise_exception=True), name='dispatch')
# Crear DocumentType (AJAX)
class GestionarDocumentTypeView(CreateView):
    model = DocumentType
    form_class = DocumentTypeForm
    template_name = 'document/registration_document.html'
    success_url = reverse_lazy('listar_documentos')

    # En GestionarDocumentTypeView (CreateView)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['editar'] = False  # Indica que es creación
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True})
        return response

    def form_invalid(self, form):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'errors': form.errors})
        return super().form_invalid(form)

# Editar DocumentType (AJAX)
class EditarDocumentTypeView(UpdateView):
    model = DocumentType
    form_class = DocumentTypeForm
    template_name = 'document/registration_document.html'
    success_url = reverse_lazy('listar_documentos')

    # En EditarDocumentTypeView (UpdateView)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['editar'] = True  # Indica que es edición
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True})
        return response

    def form_invalid(self, form):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'errors': form.errors})
        return super().form_invalid(form)
    
class ListarDocumentTypesView(ListView):
    model = DocumentType
    template_name = 'document/list_document_types.html'
    context_object_name = 'document_types'
    ordering = ['document_type']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = DocumentTypeForm()  # Agregar el formulario al contexto
        context['url_boton'] = reverse_lazy('gestionar_documento')
        context['accionBoton'] = 'modal'  # Cambia a 'redirect' si quieres redirigir
        return context

    def get(self, request, *args, **kwargs):
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            lista_documentos = []
            for documento in self.get_queryset():
                data_documento = {
                    "id": documento.id_document,
                    "document_type": documento.document_type,
                    "document_description": documento.document_description,
                    "created_at": documento.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    "update_at": documento.update_at.strftime("%Y-%m-%d %H:%M:%S")
                }
                lista_documentos.append(data_documento)
            return JsonResponse({'data': lista_documentos})
        else:
            return super().get(request, *args, **kwargs)

@method_decorator(permission_required('user.delete_documenttype', raise_exception=True), name='dispatch')
# Eliminar DocumentType (AJAX)
class EliminarDocumentTypeView(DeleteView):
    model = DocumentType
    success_url = reverse_lazy('listar_documentos')

    def post(self, request, *args, **kwargs):  # Cambiamos delete por post
        self.object = self.get_object()
        self.object.delete()
        return JsonResponse({
            'success': True,
            'message': 'Documento eliminado correctamente'
        })

@method_decorator(permission_required(['user.add_specialty', 'user.change_specialty'], raise_exception=True), name='dispatch')
class GestionarEspecialidadView(CreateView):
    model = Specialties
    form_class = SpecialtiesForm
    template_name = 'speciality/registration_especiality.html'
    success_url = reverse_lazy('listar_espacialidades')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['editar'] = False # Indica que es creación
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True, 
                'message': 'Especialidad creada correctamente'
            })
        return response

    def form_invalid(self, form):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False, 
                'errors': form.errors
            })
        return super().form_invalid(form)

@method_decorator(permission_required('user.change_specialty', raise_exception=True), name='dispatch')
class EditarEspecialidadView(UpdateView):
    model = Specialties
    form_class = SpecialtiesForm
    template_name = 'speciality/registration_especiality.html'
    success_url = reverse_lazy('listar_espacialidades')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['editar'] = True  # Indica que es edición
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True, 
                'message': 'Especialidad actualizada correctamente'
            })
        return response

    def form_invalid(self, form):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False, 
                'errors': form.errors
            })
        return super().form_invalid(form)

class ListarEspecialidadView(ListView):
    model = Specialties
    template_name = 'speciality/list_especialities.html'
    context_object_name = 'specialities'
    ordering = ['specialties']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = SpecialtiesForm()
        context['url_boton'] = reverse_lazy('gestionar_especialidad')
        context['accionBoton'] = 'modal'
        return context

    def get(self, request, *args, **kwargs):
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            # Optimización para respuesta AJAX
            queryset = self.get_queryset()

            # Formateo de datos con mejor manejo de fechas y seguridad
            data = [{
                'id_specialty': esp.id_specialty,
                'specialties': esp.specialties,
                'created_at': esp.created_at.strftime("%Y-%m-%d %H:%M:%S") if esp.created_at else None,
                'update_at': esp.update_at.strftime("%Y-%m-%d %H:%M:%S") if esp.update_at else None,
                # Agrega más campos si es necesario
            } for esp in queryset]

            # Configuración de respuesta JSON segura
            return JsonResponse(
                {
                    'data': data,
                    'recordsTotal': queryset.count(),
                    'recordsFiltered': queryset.count(),  # Para compatibilidad con DataTables
                    'draw': request.GET.get('draw', 1)     # Parámetro típico de DataTables
                },
                safe=False
            )

        # Comportamiento normal para renderizado HTML
        return super().get(request, *args, **kwargs)

@method_decorator(permission_required('user.delete_specialty', raise_exception=True), name='dispatch')
class EliminarEspecialidadView(DeleteView):
    model = Specialties
    success_url = reverse_lazy('listar_especialidades')

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        return JsonResponse({
            'success': True,
            'message': 'Especialidad eliminada correctamente'
        })


@method_decorator(permission_required(['user.add_accesslevel', 'user.change_accesslevel'], raise_exception=True), name='dispatch')
class GestionarNivelAccesoView(CreateView):
    model = AccessLevel
    form_class = AccessLevelForm
    template_name = 'access_level/registration_access_level.html'
    success_url = reverse_lazy('listar_nivel_acceso')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['editar'] = False  # Indica que es creación
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True, 
                'message': 'Nivel de acceso creado correctamente'
            })
        return response

    def form_invalid(self, form):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False, 
                'errors': form.errors
            })
        return super().form_invalid(form)

@method_decorator(permission_required('user.change_accesslevel', raise_exception=True), name='dispatch')
class EditarNivelAccesoView(UpdateView):
    model = AccessLevel
    form_class = AccessLevelForm
    template_name = 'access_level/registration_access_level.html'
    success_url = reverse_lazy('listar_nivel_acceso')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['editar'] = True  # Indica que es edición
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True, 
                'message': 'Nivel de acceso actualizado correctamente'
            })
        return response

    def form_invalid(self, form):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False, 
                'errors': form.errors
            })
        return super().form_invalid(form)

class ListarNivelAccesoView(ListView):
    model = AccessLevel
    template_name = 'access_level/list_access_levels.html'
    context_object_name = 'access_levels'
    ordering = ['access_level']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = AccessLevelForm()
        context['url_boton'] = reverse_lazy('gestionar_nivel_acceso')
        context['accionBoton'] = 'modal'
        return context

    def get(self, request, *args, **kwargs):
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            queryset = self.get_queryset()
            
            data = [{
                'id_access_level': nivel.id_access_level,
                'access_level': nivel.access_level,
                'created_at': nivel.created_at.strftime("%Y-%m-%d %H:%M:%S") if nivel.created_at else None,
                'update_at': nivel.update_at.strftime("%Y-%m-%d %H:%M:%S") if nivel.update_at else None,
            } for nivel in queryset]
            
            return JsonResponse(
                {
                    'data': data,
                    'recordsTotal': queryset.count(),
                    'recordsFiltered': queryset.count(),
                    'draw': request.GET.get('draw', 1)
                },
                safe=False
            )
        
        return super().get(request, *args, **kwargs)

@method_decorator(permission_required('user.delete_accesslevel', raise_exception=True), name='dispatch')
class EliminarNivelAccesoView(DeleteView):
    model = AccessLevel
    success_url = reverse_lazy('listar_nivel_acceso')

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        return JsonResponse({
            'success': True,
            'message': 'Nivel de acceso eliminado correctamente'
        })

class CambiarContrasenaView(PasswordChangeView):
    form_class = CustomPasswordChangeForm #Usar el formulario personalizado
    template_name = 'user/change_password.html'
    success_url = reverse_lazy('perfil_usuario')
