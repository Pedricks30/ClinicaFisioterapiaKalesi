# citas/views.py
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
from users.models import CustomUser


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
        print("=" * 50)
        print("Datos recibidos:")
        for key, value in request.POST.items():
            print(f"  {key}: {value}")
        print("=" * 50)

        fecha_recibida = request.POST.get('fecha')
        print(f"🔴 Fecha recibida: {fecha_recibida}")

        profesional_id = request.POST.get('profesional_id')
        if not profesional_id:
            return JsonResponse({'success': False, 'error': 'Profesional no especificado'}, status=400)
        
        profesional = get_object_or_404(CustomUser, pk=profesional_id)
        
        # ✅ Verificar si se está forzando finalización
        forzar_finalizacion = request.POST.get('forzar_finalizacion', 'false') == 'true'
        
        # ✅ Si es finalización forzada, validar que el paciente sea apto
        if forzar_finalizacion:
            paciente_id = request.POST.get('paciente')
            if paciente_id:
                from .api_views import verificar_puede_finalizar
                # Verificar si el paciente puede ser finalizado
                try:
                    paciente = get_object_or_404(CustomUser, pk=paciente_id)
                    # La verificación se hará en el formulario
                except:
                    pass
        
        # ✅ Crear el formulario con los datos recibidos
        form = CitaModalForm(
            request.POST,
            profesional=profesional,
            creada_por=request.user,
            forzar_finalizacion=forzar_finalizacion,
        )
        
        if form.is_valid():
            try:
                cita = form.save()
                return JsonResponse({
                    'success': True,
                    'message': 'Cita creada exitosamente',
                    'cita_id': cita.id,
                    'tipo_cita': cita.tipo_cita,
                    'numero_sesion': cita.numero_sesion
                })
            except Exception as e:
                print(f"❌ Error al guardar la cita: {str(e)}")
                return JsonResponse({
                    'success': False, 
                    'error': f'Error al guardar: {str(e)}'
                }, status=400)
        
        # Log de errores para debugging
        print("❌ Errores del formulario:", form.errors)
        return JsonResponse({
            'success': False, 
            'errors': form.errors
        }, status=400)


# =============================================================================
# EDITAR CITA (DESDE EL MODAL - AJAX)
# =============================================================================
class CitaUpdateAjaxView(LoginRequiredMixin, View):
    """
    Actualiza una cita desde el modal del calendario vía AJAX.
    """
    def post(self, request, pk, *args, **kwargs):
        cita = get_object_or_404(Cita, pk=pk)
        
        # ✅ Verificar si el tipo_cita viene en el POST
        tipo_cita = request.POST.get('tipo_cita')
        if not tipo_cita:
            return JsonResponse({
                'success': False, 
                'error': 'Tipo de cita no especificado'
            }, status=400)
        
        # ✅ Crear formulario con los datos recibidos
        form = CitaModalForm(
            request.POST,
            instance=cita,
            profesional=cita.profesional,
            creada_por=request.user,
            forzar_finalizacion=False,  # Nunca forzar finalización en edición
        )
        
        if form.is_valid():
            try:
                cita_actualizada = form.save()
                return JsonResponse({
                    'success': True,
                    'message': 'Cita actualizada exitosamente',
                    'cita_id': cita_actualizada.id,
                    'tipo_cita': cita_actualizada.tipo_cita,
                    'numero_sesion': cita_actualizada.numero_sesion
                })
            except Exception as e:
                print(f"❌ Error al actualizar la cita: {str(e)}")
                return JsonResponse({
                    'success': False, 
                    'error': f'Error al actualizar: {str(e)}'
                }, status=400)
        
        print("❌ Errores del formulario (edición):", form.errors)
        return JsonResponse({
            'success': False, 
            'errors': form.errors
        }, status=400)


# =============================================================================
# ELIMINAR CITA (AJAX)
# =============================================================================
class CitaDeleteAjaxView(LoginRequiredMixin, View):
    """
    Elimina/cancela una cita vía AJAX.
    """
    def post(self, request, pk, *args, **kwargs):
        cita = get_object_or_404(Cita, pk=pk)
        
        # ✅ Verificar si la cita puede ser cancelada
        if not cita.puede_ser_cancelada:
            return JsonResponse({
                'success': False,
                'error': 'La cita no puede ser cancelada. Mínimo 24 horas de anticipación.'
            }, status=400)
        
        try:
            cita.cancelar(request.user)
            return JsonResponse({
                'success': True, 
                'message': 'Cita cancelada exitosamente'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Error al cancelar: {str(e)}'
            }, status=400)


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
        
        user = self.request.user
        if user.tipo_usuario in ['MEDIC', 'FISIO']:
            queryset = queryset.filter(profesional=user)
        
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
        
        # ✅ Agregar conteo de citas por tipo para estadísticas
        citas = self.get_queryset()
        context['total_citas'] = citas.count()
        context['citas_por_tipo'] = {}
        for tipo, label in Cita.TIPO_CITA_FISIOTERAPIA:
            count = citas.filter(tipo_cita=tipo).count()
            if count > 0:
                context['citas_por_tipo'][label] = count
        
        return context


# =============================================================================
# DETALLE DE CITA
# =============================================================================
class CitaDetailView(LoginRequiredMixin, DetailView):
    """
    Muestra el detalle de una cita específica.
    """
    model = Cita
    template_name = 'citas/cita_detail.html'
    context_object_name = 'cita'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cita = self.object
        
        # ✅ Historial de cambios
        context['historico'] = cita.historico.all().order_by('-created_at')[:10]
        
        # ✅ Verificar si el usuario puede editar
        user = self.request.user
        context['puede_editar'] = (
            user.tipo_usuario in ['ADMIN', 'MEDIC', 'FISIO'] or
            user == cita.creada_por
        )
        
        # ✅ Verificar si el usuario puede cancelar
        context['puede_cancelar'] = cita.puede_ser_cancelada and (
            user.tipo_usuario in ['ADMIN', 'MEDIC', 'FISIO', 'RECEP'] or
            user == cita.creada_por
        )
        
        # ✅ Verificar si el usuario puede iniciar/completar
        context['puede_iniciar'] = cita.puede_iniciar and (
            user.tipo_usuario in ['ADMIN', 'MEDIC', 'FISIO']
        )
        
        # ✅ Obtener información del expediente
        try:
            expediente = cita.paciente.expediente
            context['expediente'] = expediente
            context['tiene_primera_consulta'] = hasattr(expediente, 'primera_consulta')
            context['total_seguimientos'] = expediente.seguimientos.count()
            context['tiene_finalizacion'] = hasattr(expediente, 'finalizacion')
        except:
            context['expediente'] = None
        
        return context


# =============================================================================
# VISTAS ADICIONALES PARA ACCIONES RÁPIDAS (OPCIONAL)
# =============================================================================

class CitaConfirmarAjaxView(LoginRequiredMixin, View):
    """
    Confirma una cita vía AJAX.
    """
    def post(self, request, pk, *args, **kwargs):
        cita = get_object_or_404(Cita, pk=pk)
        
        # ✅ Verificar permisos
        if request.user.tipo_usuario not in ['ADMIN', 'MEDIC', 'FISIO', 'RECEP']:
            return JsonResponse({
                'success': False,
                'error': 'No tienes permisos para confirmar citas'
            }, status=403)
        
        if cita.estado != 'PENDIENTE':
            return JsonResponse({
                'success': False,
                'error': 'Solo se pueden confirmar citas en estado PENDIENTE'
            }, status=400)
        
        try:
            cita.confirmar(request.user)
            return JsonResponse({
                'success': True,
                'message': 'Cita confirmada exitosamente'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Error al confirmar: {str(e)}'
            }, status=400)


class CitaIniciarAjaxView(LoginRequiredMixin, View):
    """
    Inicia una cita (marca como EN_PROCESO) vía AJAX.
    """
    def post(self, request, pk, *args, **kwargs):
        cita = get_object_or_404(Cita, pk=pk)
        
        # ✅ Solo MEDIC y FISIO pueden iniciar citas
        if request.user.tipo_usuario not in ['ADMIN', 'MEDIC', 'FISIO']:
            return JsonResponse({
                'success': False,
                'error': 'No tienes permisos para iniciar citas'
            }, status=403)
        
        if not cita.puede_iniciar:
            return JsonResponse({
                'success': False,
                'error': 'La cita no puede ser iniciada en este momento'
            }, status=400)
        
        try:
            cita.iniciar(request.user)
            return JsonResponse({
                'success': True,
                'message': 'Cita iniciada exitosamente'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Error al iniciar: {str(e)}'
            }, status=400)


class CitaCompletarAjaxView(LoginRequiredMixin, View):
    """
    Completa una cita vía AJAX.
    """
    def post(self, request, pk, *args, **kwargs):
        cita = get_object_or_404(Cita, pk=pk)
        
        # ✅ Solo MEDIC y FISIO pueden completar citas
        if request.user.tipo_usuario not in ['ADMIN', 'MEDIC', 'FISIO']:
            return JsonResponse({
                'success': False,
                'error': 'No tienes permisos para completar citas'
            }, status=403)
        
        if cita.estado != 'EN_PROCESO':
            return JsonResponse({
                'success': False,
                'error': 'Solo se pueden completar citas en estado EN_PROCESO'
            }, status=400)
        
        try:
            cita.completar(request.user)
            return JsonResponse({
                'success': True,
                'message': 'Cita completada exitosamente'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Error al completar: {str(e)}'
            }, status=400)