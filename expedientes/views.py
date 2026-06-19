# expedientes/views.py
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.generic import DetailView, TemplateView
from django.views.generic.edit import CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from datetime import timedelta
from django.core.exceptions import PermissionDenied
from django.contrib import messages

from citas.models import Cita
from paciente.models import Patient
from .models import ConsultaFinalizacion, ConsultaSegumiento, Expediente, PrimeraConsulta
from .forms import PrimeraConsultaForm, ConsultaSegumientoForm, ConsultaFinalizacionForm

# Obtener cuestionarios disponibles por tipo
from cuestionarios.models import Cuestionario, PreguntaCuestionario, RespuestaCuestionario
from django.http import JsonResponse
from django.template.loader import render_to_string  # <-- Asegúrate de importar esto
import json
from django.core.serializers.json import DjangoJSONEncoder

# ============================================================================
# VISTAS BASADAS EN FUNCIONES
# ============================================================================

@login_required
def expediente_wizard(request, expediente_id):
    """Redirige al wizard del expediente - sección datos"""
    return redirect('expedientes:expediente_datos', expediente_id=expediente_id)


@login_required
def crear_nueva_sesion(request, expediente_id):
    """Vista para que el médico agregue una nueva sesión cuando lo considere necesario"""
    expediente = get_object_or_404(Expediente, id=expediente_id)
    messages.warning(request, 'Funcionalidad en desarrollo. Por favor use el panel de administración.')
    return redirect('expediente_detail', expediente_id)


@require_http_methods(["DELETE"])
@login_required
def eliminar_acto_clinico(request, tipo, id_acto):
    """Endpoint AJAX para eliminar actos clínicos"""
    
    # Verificar que el usuario sea ADMIN, MEDIC o FISIO
    if request.user.tipo_usuario not in ['ADMIN', 'MEDIC', 'FISIO']:
        return JsonResponse({'success': False, 'error': 'No tiene permisos para eliminar'}, status=403)
    
    try:
        if tipo == 'primera':
            acto = PrimeraConsulta.objects.get(id=id_acto)
            acto.delete()
        elif tipo == 'seguimiento':
            acto = ConsultaSegumiento.objects.get(id=id_acto)
            acto.delete()
        elif tipo == 'finalizacion':
            acto = ConsultaFinalizacion.objects.get(id=id_acto)
            acto.delete()
        else:
            return JsonResponse({'success': False, 'error': 'Tipo no válido'}, status=400)
        
        return JsonResponse({'success': True, 'message': 'Eliminado correctamente'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# ============================================================================
# CLASE BASE PARA VERIFICAR PERMISOS
# ============================================================================

class BaseExpedienteActoView:
    """Clase base para verificar permisos de ADMIN, MEDIC y FISIO"""
    
    def verificar_permiso(self, request):
        """Verifica si el usuario tiene permiso para gestionar actos clínicos"""
        if request.user.tipo_usuario not in ['ADMIN', 'MEDIC', 'FISIO']:
            raise PermissionDenied
        return True
    
    def puede_crear_historias_pasadas(self, user):
        """Solo ADMIN puede crear historias de fechas pasadas"""
        return user.tipo_usuario == 'ADMIN'


# ============================================================================
# VISTAS BASADAS EN CLASES
# ============================================================================

class ExpedienteDetailView(DetailView):
    model = Expediente
    template_name = 'expedientes/detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        expediente = self.object
        
        context['primera_consulta'] = getattr(expediente, 'primera_consulta', None)
        context['seguimientos'] = expediente.seguimientos.all().order_by('numero_sesion')
        context['total_sesiones'] = expediente.seguimientos.count()
        context['finalizacion'] = getattr(expediente, 'finalizacion', None)
        
        if context['seguimientos']:
            evolucion_dolor = [
                {
                    'sesion': s.numero_sesion,
                    'dolor': s.nivel_dolor_actual,
                    'fecha': s.fecha_consulta.strftime('%d/%m/%Y')
                }
                for s in context['seguimientos']
            ]
            context['evolucion_dolor'] = evolucion_dolor
            
            primera = context['primera_consulta']
            ultima = context['seguimientos'].last()
            if primera and ultima:
                mejoria = primera.nivel_dolor_inicial - ultima.nivel_dolor_actual
                if primera.nivel_dolor_inicial > 0:
                    porcentaje = (mejoria / primera.nivel_dolor_inicial) * 100
                    context['porcentaje_mejoria'] = round(porcentaje, 1)
            
            fase_1 = list(context['seguimientos'])[:3]
            fase_2 = list(context['seguimientos'])[3:6] if len(context['seguimientos']) > 3 else []
            
            if fase_1:
                context['promedio_inicial'] = sum(s.nivel_dolor_actual for s in fase_1) / len(fase_1)
            if fase_2:
                context['promedio_intermedio'] = sum(s.nivel_dolor_actual for s in fase_2) / len(fase_2)
        
        return context


class ExpedienteDatosView(TemplateView):
    """Vista para mostrar los datos del paciente dentro del expediente"""
    template_name = 'expedientes/expediente_datos_paciente.html'
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.has_perm('paciente.view_patient'):
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        expediente_id = self.kwargs.get('expediente_id')
        context['expediente'] = get_object_or_404(Expediente, id=expediente_id)
        context['paciente'] = context['expediente'].paciente
        context['seccion'] = 'datos'
        return context


@method_decorator(login_required, name='dispatch')
class ExpedienteCitasView(TemplateView):
    """Vista para mostrar las citas del paciente dentro del expediente"""
    template_name = 'expedientes/expediente_citas_paciente.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        expediente_id = self.kwargs.get('expediente_id')
        context['expediente'] = get_object_or_404(Expediente, id=expediente_id)
        context['paciente'] = context['expediente'].paciente
        context['seccion'] = 'citas'
        
        user = self.request.user
        citas = Cita.objects.filter(
            paciente=context['paciente']
        ).select_related(
            'profesional',
            'profesional__perfil_medico',
            'profesional__perfil_medico__specialties',
            'profesional__perfil_fisioterapeuta',
            'profesional__perfil_fisioterapeuta__specialties'
        )
        
        if user.tipo_usuario in ['MEDIC', 'FISIO']:
            citas = citas.filter(profesional=user)
        
        context['citas'] = citas.order_by('-fecha')
        
        return context


class ExpedienteActosView(TemplateView):
    template_name = 'expedientes/expediente_actos_clinicos_paciente.html'
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.tipo_usuario not in ['ADMIN', 'MEDIC', 'FISIO']:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        expediente_id = self.kwargs.get('expediente_id')
        expediente = get_object_or_404(Expediente, id=expediente_id)
        paciente = expediente.paciente
        user = self.request.user
        es_admin = user.tipo_usuario == 'ADMIN'
        es_medic = user.tipo_usuario == 'MEDIC'
        
        # ✅ ADMIN puede ver TODAS las citas no canceladas
        # ✅ MEDIC/FISIO solo ven citas de los últimos 7 días
        if es_admin:
            citas_disponibles = Cita.objects.filter(
                paciente=paciente
            ).exclude(
                estado__in=['CANCELADA', 'NO_ASISTIO']  # ✅ Excluir CANCELADA y NO_ASISTIO
            ).select_related('profesional').order_by('-fecha')
        else:
            fecha_limite = timezone.now().date() - timedelta(days=7)
            citas_disponibles = Cita.objects.filter(
                paciente=paciente,
                estado__in=['PENDIENTE', 'CONFIRMADA', 'COMPLETADA'],  # ✅ Incluir COMPLETADA también
                fecha__date__gte=fecha_limite
            ).exclude(
                estado__in=['CANCELADA', 'NO_ASISTIO']  # ✅ Excluir CANCELADA y NO_ASISTIO
            ).select_related('profesional')
        
        # Filtrar citas que ya tienen historia clínica
        ids_con_historia = []
        
        if hasattr(expediente, 'primera_consulta') and expediente.primera_consulta.cita:
            ids_con_historia.append(expediente.primera_consulta.cita.id)
        
        for seguimiento in expediente.seguimientos.all():
            if seguimiento.cita:
                ids_con_historia.append(seguimiento.cita.id)
        
        if hasattr(expediente, 'finalizacion') and expediente.finalizacion.cita:
            ids_con_historia.append(expediente.finalizacion.cita.id)
        
        citas_disponibles = citas_disponibles.exclude(id__in=ids_con_historia)
        
        # Procesar citas disponibles
        hoy = timezone.now().date()
        
        citas_con_tipo = []
        for cita in citas_disponibles:
            fecha_cita = cita.fecha.date()
            dias_diferencia = (hoy - fecha_cita).days
            
            # ADMIN puede crear historias de cualquier fecha pasada
            # Los demás solo de hoy o últimos 7 días
            puede_crear = es_admin or (dias_diferencia <= 7)
            
            if cita.tipo_cita == 'PRIMERA_CONSULTA':
                tipo_historia = 'primera'
                nombre_tipo = 'Primera Consulta'
                url_crear = reverse('expedientes:crear_primera_consulta', args=[expediente.id, cita.id])
            elif cita.tipo_cita == 'SEGUIMIENTO':
                tipo_historia = 'seguimiento'
                nombre_tipo = 'Seguimiento'
                url_crear = reverse('expedientes:crear_seguimiento', args=[expediente.id, cita.id])
            elif cita.tipo_cita == 'FINALIZACION':
                tipo_historia = 'finalizacion'
                nombre_tipo = 'Finalización'
                url_crear = reverse('expedientes:crear_finalizacion', args=[expediente.id, cita.id])
            else:
                continue
            
            citas_con_tipo.append({
                'cita': cita,
                'tipo': tipo_historia,
                'nombre_tipo': nombre_tipo,
                'puede_crear': puede_crear,
                'url_crear': url_crear,
                'fecha_cita': fecha_cita,
                'hoy': hoy,
                'dias_atras': dias_diferencia,
            })
        
        # Obtener historias existentes
        historias = []
        
        if hasattr(expediente, 'primera_consulta'):
            historia = expediente.primera_consulta
            puede_editar = self._puede_editar(historia, user)
            # ✅ Un MEDIC solo puede eliminar si fue él quien creó la historia
            puede_eliminar = es_admin or (es_medic and historia.profesional == user)
            
            historias.append({
                'id': historia.id,
                'tipo': 'primera',
                'nombre_tipo': 'Primera Consulta',
                'fecha': historia.fecha_consulta,
                'profesional': historia.profesional,
                'cita': historia.cita,
                'url_editar': reverse('expedientes:editar_primera_consulta', args=[expediente.id, historia.id]),
                'url_eliminar': reverse('expedientes:eliminar_acto_clinico', args=['primera', historia.id]),
                'puede_editar': puede_editar,
                'puede_eliminar': puede_eliminar,
                'created_at': historia.created_at,
                'es_creador': historia.profesional == user,  # ✅ Para saber si fue él quien la creó
            })
        
        for seguimiento in expediente.seguimientos.all():
            puede_editar = self._puede_editar(seguimiento, user)
            # ✅ Un MEDIC solo puede eliminar si fue él quien creó la historia
            puede_eliminar = es_admin or (es_medic and seguimiento.profesional == user)
            
            historias.append({
                'id': seguimiento.id,
                'tipo': 'seguimiento',
                'nombre_tipo': f'Seguimiento - Sesión {seguimiento.numero_sesion}',
                'fecha': seguimiento.fecha_consulta,
                'profesional': seguimiento.profesional,
                'cita': seguimiento.cita,
                'url_editar': reverse('expedientes:editar_seguimiento', args=[expediente.id, seguimiento.id]),
                'url_eliminar': reverse('expedientes:eliminar_acto_clinico', args=['seguimiento', seguimiento.id]),
                'puede_editar': puede_editar,
                'puede_eliminar': puede_eliminar,
                'created_at': seguimiento.created_at,
                'numero_sesion': seguimiento.numero_sesion,
                'es_creador': seguimiento.profesional == user,  # ✅ Para saber si fue él quien la creó
            })
        
        if hasattr(expediente, 'finalizacion'):
            historia = expediente.finalizacion
            puede_editar = self._puede_editar(historia, user)
            # ✅ Un MEDIC solo puede eliminar si fue él quien creó la historia
            puede_eliminar = es_admin or (es_medic and historia.profesional == user)
            
            historias.append({
                'id': historia.id,
                'tipo': 'finalizacion',
                'nombre_tipo': 'Finalización',
                'fecha': historia.fecha_consulta,
                'profesional': historia.profesional,
                'cita': historia.cita,
                'url_editar': reverse('expedientes:editar_finalizacion', args=[expediente.id, historia.id]),
                'url_eliminar': reverse('expedientes:eliminar_acto_clinico', args=['finalizacion', historia.id]),
                'puede_editar': puede_editar,
                'puede_eliminar': puede_eliminar,
                'created_at': historia.created_at,
                'es_creador': historia.profesional == user,  # ✅ Para saber si fue él quien la creó
            })
        
        historias.sort(key=lambda x: x['fecha'], reverse=True)
        
        context['expediente'] = expediente
        context['paciente'] = paciente
        context['seccion'] = 'actos'
        context['citas_disponibles'] = citas_con_tipo
        context['historias'] = historias
        context['es_admin'] = es_admin
        context['es_medic'] = es_medic
        context['ahora'] = timezone.now()
        
        return context
    
    def _puede_editar(self, historia, user):
        """Verifica si la historia puede ser editada"""
        if user.tipo_usuario == 'ADMIN':
            return True
        tiempo_transcurrido = timezone.now() - historia.created_at
        return tiempo_transcurrido < timedelta(hours=1)


# expedientes/views.py - Agregar al final del archivo
class ExpedienteEvolucionGraficaView(LoginRequiredMixin, TemplateView):
    """Vista para mostrar la evolución gráfica del paciente"""
    template_name = 'expedientes/expediente_evolucion_grafica_paciente.html'
    
    def dispatch(self, request, *args, **kwargs):
        self.expediente = get_object_or_404(Expediente, id=kwargs['expediente_id'])
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        expediente = self.expediente
        
        from cuestionarios.models import EvolucionPaciente, AnalisisPredictivoEscala, PreguntaCuestionario, RespuestaCuestionario
        from collections import defaultdict
        
        # ============================================
        # OBTENER TODAS LAS EVOLUCIONES DEL PACIENTE
        # ============================================
        evoluciones = EvolucionPaciente.objects.filter(expediente=expediente)
        
        datos_graficos = []
        for evol in evoluciones:
            # Verificar que evolucion_historica sea una lista
            historica = evol.evolucion_historica
            if isinstance(historica, str):
                try:
                    historica = json.loads(historica)
                except:
                    historica = []
            elif not isinstance(historica, list):
                historica = []
            
            # Obtener el título de la pregunta
            titulo = evol.tipo_evaluacion
            if evol.pregunta_relacionada:
                titulo = evol.pregunta_relacionada.texto_pregunta
            
            datos_graficos.append({
                'id': evol.id,
                'titulo': titulo,
                'datos': historica if historica else [],
                'tendencia': evol.tendencia_general,
                'mejoria': evol.porcentaje_mejoria,
                'mejor_valor': evol.mejor_valor,
                'peor_valor': evol.peor_valor,
                'promedio': round(evol.promedio, 2),
                'pregunta_id': evol.pregunta_relacionada.id if evol.pregunta_relacionada else None,
            })
        
        # ============================================
        # CALCULAR PROMEDIO POR SESIÓN (GRÁFICO PRINCIPAL)
        # ============================================
        # Diccionario para almacenar los valores por sesión
        valores_por_sesion = defaultdict(list)
        fechas_por_sesion = {}
        
        # Recorrer todas las respuestas de escala del paciente
        respuestas = RespuestaCuestionario.objects.filter(
            consulta_seguimiento__expediente=expediente,
            pregunta__tipo_pregunta__in=['ESCALA', 'ESCALA_NUMERICA'],
            respuesta_escala__isnull=False
        ).select_related('consulta_seguimiento', 'pregunta')
        
        for respuesta in respuestas:
            sesion = respuesta.consulta_seguimiento
            sesion_num = sesion.numero_sesion
            valores_por_sesion[sesion_num].append(respuesta.respuesta_escala)
            fechas_por_sesion[sesion_num] = sesion.fecha_consulta.strftime('%d/%m/%Y')
        
        # Calcular promedio por sesión
        promedio_por_sesion = []
        for sesion_num in sorted(valores_por_sesion.keys()):
            valores = valores_por_sesion[sesion_num]
            promedio = sum(valores) / len(valores) if valores else 0
            promedio_por_sesion.append({
                'sesion': sesion_num,
                'fecha': fechas_por_sesion.get(sesion_num, ''),
                'valor': round(promedio, 1),
                'total_preguntas': len(valores)
            })
        
        # Calcular tendencia de la gráfica principal
        if len(promedio_por_sesion) >= 2:
            valores = [p['valor'] for p in promedio_por_sesion]
            if valores[-1] < valores[0]:
                tendencia_principal = 'MEJORANDO'
            elif valores[-1] > valores[0]:
                tendencia_principal = 'EMPEORANDO'
            else:
                tendencia_principal = 'ESTABLE'
        else:
            tendencia_principal = 'SIN_DATOS'
        
        # Calcular mejoría total de la gráfica principal
        if len(promedio_por_sesion) >= 2:
            primero = promedio_por_sesion[0]['valor']
            ultimo = promedio_por_sesion[-1]['valor']
            if primero > 0:
                mejoria_principal = ((primero - ultimo) / primero * 100)
            else:
                mejoria_principal = 0
        else:
            mejoria_principal = 0
        
        # ============================================
        # OBTENER TODAS LAS PREDICCIONES
        # ============================================
        predicciones_qs = AnalisisPredictivoEscala.objects.filter(
            consulta_seguimiento__expediente=expediente,
            prediccion_siguiente__isnull=False
        ).select_related('pregunta').order_by('pregunta__orden')
        
        predicciones = []
        for pred in predicciones_qs:
            predicciones.append({
                'id': pred.id,
                'pregunta_id': pred.pregunta.id,
                'pregunta_texto': pred.pregunta.texto_pregunta if pred.pregunta else '',
                'prediccion_siguiente': pred.prediccion_siguiente,
                'intervalo_confianza_min': pred.intervalo_confianza_min,
                'intervalo_confianza_max': pred.intervalo_confianza_max,
                'tendencia': pred.tendencia,
                'valor_escala': pred.valor_escala,
            })
        
        # ============================================
        # CONTEXTO PARA EL TEMPLATE
        # ============================================
        context.update({
            'expediente': expediente,
            'paciente': expediente.paciente,
            'seccion': 'evolucion',
            'datos_graficos_json': json.dumps(datos_graficos, cls=DjangoJSONEncoder),
            'predicciones_json': json.dumps(predicciones, cls=DjangoJSONEncoder),
            'promedio_por_sesion_json': json.dumps(promedio_por_sesion, cls=DjangoJSONEncoder),
            'tendencia_principal': tendencia_principal,
            'mejoria_principal': round(mejoria_principal, 1),
            'total_evoluciones': evoluciones.count(),
            'total_sesiones': expediente.seguimientos.count(),
            'total_preguntas_escala': RespuestaCuestionario.objects.filter(
                consulta_seguimiento__expediente=expediente,
                pregunta__tipo_pregunta__in=['ESCALA', 'ESCALA_NUMERICA'],
                respuesta_escala__isnull=False
            ).count(),
        })
        
        return context
# ============================================================================
# PRIMERA CONSULTA
# ============================================================================

# expedientes/views.py

class CrearPrimeraConsultaView(LoginRequiredMixin, BaseExpedienteActoView, CreateView):
    model = PrimeraConsulta
    form_class = PrimeraConsultaForm
    template_name = 'expedientes/actos/primera_consulta_form.html'
    
    def dispatch(self, request, *args, **kwargs):
        try:
            self.expediente = get_object_or_404(Expediente, id=kwargs['expediente_id'])
            self.cita = get_object_or_404(Cita, id=kwargs['cita_id'])
            
            es_admin = request.user.tipo_usuario == 'ADMIN'
            
            # Para ADMIN: Saltar validaciones de fecha
            if not es_admin:
                fecha_cita = self.cita.fecha.date()
                hoy = timezone.now().date()
                
                if fecha_cita != hoy:
                    messages.error(request, 'Solo puedes crear la historia clínica el día de la cita.')
                    return redirect('expedientes:expediente_actos', expediente_id=self.expediente.id)
            
            # Verificar que la cita no esté cancelada
            if self.cita.estado == 'CANCELADA':
                messages.error(request, 'No puedes crear una historia clínica para una cita cancelada.')
                return redirect('expedientes:expediente_actos', expediente_id=self.expediente.id)
            
            # Verificar que sea primera consulta
            if self.cita.tipo_cita != 'PRIMERA_CONSULTA':
                messages.error(request, 'Esta cita no es de tipo Primera Consulta.')
                return redirect('expedientes:expediente_actos', expediente_id=self.expediente.id)
            
            # Verificar que no exista ya
            if hasattr(self.expediente, 'primera_consulta'):
                messages.error(request, 'Este paciente ya tiene una Primera Consulta registrada.')
                return redirect('expedientes:expediente_actos', expediente_id=self.expediente.id)
            
            return super().dispatch(request, *args, **kwargs)
            
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
            return redirect('expedientes:expediente_actos', expediente_id=kwargs.get('expediente_id'))
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['expediente'] = self.expediente
        context['expediente_id'] = self.expediente.id
        context['paciente'] = self.expediente.paciente
        context['cita'] = self.cita
        context['titulo'] = 'Primera Consulta'
        context['accion'] = 'Crear'
        context['es_admin'] = self.request.user.tipo_usuario == 'ADMIN'
        return context
    
    def form_valid(self, form):
        """Guarda el formulario correctamente"""
        form.instance.expediente = self.expediente
        form.instance.profesional = self.request.user
        form.instance.cita = self.cita
        form.instance.fecha_consulta = timezone.now()
        
        # Guardar
        self.object = form.save()
        
        # Actualizar estado de la cita
        self.cita.estado = 'COMPLETADA'
        self.cita.save(update_fields=['estado'])
        
        messages.success(self.request, 'Primera Consulta creada exitosamente. La cita ha sido marcada como COMPLETADA.')
        return redirect(self.get_success_url())
    
    def form_invalid(self, form):
        """Muestra errores del formulario"""
        from django.contrib import messages
        
        print("=== ERRORES DEL FORMULARIO ===")
        print(f"Errores: {form.errors}")
        
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f'Error en {field}: {error}')
        
        return super().form_invalid(form)
    
    def get_success_url(self):
        return reverse('expedientes:expediente_actos', args=[self.expediente.id])

class EditarPrimeraConsultaView(LoginRequiredMixin, BaseExpedienteActoView, UpdateView):
    model = PrimeraConsulta
    form_class = PrimeraConsultaForm
    template_name = 'expedientes/actos/primera_consulta_form.html'
    
    def dispatch(self, request, *args, **kwargs):
        self.verificar_permiso(request)
        
        self.acto = self.get_object()
        self.expediente = self.acto.expediente
        
        # Verificar tiempo de edición (1 hora) - ADMIN puede editar sin límite
        if request.user.tipo_usuario != 'ADMIN':
            tiempo_transcurrido = timezone.now() - self.acto.created_at
            if tiempo_transcurrido > timedelta(hours=1):
                messages.error(request, 'Solo tienes 1 hora después de crear la historia para editarla.')
                return redirect('expedientes:expediente_actos', expediente_id=self.expediente.id)
        
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['expediente'] = self.expediente
        context['paciente'] = self.expediente.paciente
        context['cita'] = self.acto.cita
        context['titulo'] = 'Primera Consulta'
        context['accion'] = 'Editar'
        context['es_admin'] = self.request.user.tipo_usuario == 'ADMIN'
        return context
    
    def form_valid(self, form):
        messages.success(self.request, 'Primera Consulta actualizada exitosamente.')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('expedientes:expediente_actos', args=[self.expediente.id])


# ============================================================================
# SEGUIMIENTO
# ============================================================================

class CrearSeguimientoView(LoginRequiredMixin, BaseExpedienteActoView, CreateView):
    model = ConsultaSegumiento
    form_class = ConsultaSegumientoForm
    template_name = 'expedientes/actos/seguimiento_form.html'
    
    def dispatch(self, request, *args, **kwargs):
        self.verificar_permiso(request)
        
        self.expediente = get_object_or_404(Expediente, id=kwargs['expediente_id'])
        self.cita = get_object_or_404(Cita, id=kwargs['cita_id'])
        
        es_admin = request.user.tipo_usuario == 'ADMIN'
        fecha_cita = self.cita.fecha.date()
        hoy = timezone.now().date()
        
        # ✅ Solo ADMIN puede crear historias de fechas pasadas
        if not es_admin:
            if fecha_cita != hoy:
                messages.error(request, 'Solo puedes crear la historia clínica el día de la cita.')
                return redirect('expedientes:expediente_actos', expediente_id=self.expediente.id)
        
        if self.cita.estado == 'CANCELADA':
            messages.error(request, 'No puedes crear una historia clínica para una cita cancelada.')
            return redirect('expedientes:expediente_actos', expediente_id=self.expediente.id)
        
        if self.cita.tipo_cita != 'SEGUIMIENTO':
            messages.error(request, 'Esta cita no es de tipo Seguimiento.')
            return redirect('expedientes:expediente_actos', expediente_id=self.expediente.id)
        
        if not hasattr(self.expediente, 'primera_consulta'):
            messages.error(request, 'Debe existir una Primera Consulta antes de crear seguimientos.')
            return redirect('expedientes:expediente_actos', expediente_id=self.expediente.id)
        
        if hasattr(self.expediente, 'finalizacion'):
            messages.error(request, 'El tratamiento ya está finalizado, no se pueden crear más seguimientos.')
            return redirect('expedientes:expediente_actos', expediente_id=self.expediente.id)
        
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['expediente'] = self.expediente
        context['paciente'] = self.expediente.paciente
        context['cita'] = self.cita
        context['titulo'] = 'Seguimiento'
        context['accion'] = 'Crear'
        context['es_admin'] = self.request.user.tipo_usuario == 'ADMIN'
        return context
    
    def form_valid(self, form):
        print("=== GUARDANDO SEGUIMIENTO ===")

        form.instance.expediente = self.expediente
        form.instance.profesional = self.request.user
        form.instance.cita = self.cita
        form.instance.fecha_consulta = timezone.now()

        # Calcular número de sesión
        ultima_sesion = ConsultaSegumiento.objects.filter(
            expediente=self.expediente
        ).order_by('-numero_sesion').first()
        form.instance.numero_sesion = (ultima_sesion.numero_sesion + 1) if ultima_sesion else 1
        print(f"Número de sesión asignado: {form.instance.numero_sesion}")

        # Guardar
        self.object = form.save()
        print(f"✅ Seguimiento guardado con ID: {self.object.id}")

        # Actualizar estado de la cita
        self.cita.estado = 'COMPLETADA'
        self.cita.save(update_fields=['estado'])
        print(f"✅ Cita {self.cita.id} marcada como COMPLETADA")

        messages.success(self.request, f'Sesión {form.instance.numero_sesion} creada exitosamente. La cita ha sido marcada como COMPLETADA.')

        # Guardar datos temporales en sesión
        self.request.session['seguimiento_data'] = {
            'form_data': self.request.POST,
            'files_data': self.request.FILES,
        }
        
        # Redirigir a la vista de cuestionarios con modelo 3D
        return redirect(
            'expedientes:seguimiento_cuestionarios',
            expediente_id=self.expediente.id,
            cita_id=self.cita.id
        )
    
    def form_invalid(self, form):
    
        print("=== ERRORES DEL FORMULARIO DE SEGUIMIENTO ===")
        print(f"Errores: {form.errors}")
        print(f"Datos enviados: {self.request.POST}")

        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f'Error en {field}: {error}')

        return super().form_invalid(form)
    
    def get_success_url(self):
        return reverse('expedientes:expediente_actos', args=[self.expediente.id])


class EditarSeguimientoView(LoginRequiredMixin, BaseExpedienteActoView, UpdateView):
    model = ConsultaSegumiento
    form_class = ConsultaSegumientoForm
    template_name = 'expedientes/actos/seguimiento_form.html'
    
    def dispatch(self, request, *args, **kwargs):
        self.verificar_permiso(request)
        
        self.acto = self.get_object()
        self.expediente = self.acto.expediente
        
        if request.user.tipo_usuario != 'ADMIN':
            tiempo_transcurrido = timezone.now() - self.acto.created_at
            if tiempo_transcurrido > timedelta(hours=1):
                messages.error(request, 'Solo tienes 1 hora después de crear la historia para editarla.')
                return redirect('expedientes:expediente_actos', expediente_id=self.expediente.id)
        
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['expediente'] = self.expediente
        context['paciente'] = self.expediente.paciente
        context['cita'] = self.acto.cita
        context['titulo'] = 'Seguimiento'
        context['accion'] = 'Editar'
        context['es_admin'] = self.request.user.tipo_usuario == 'ADMIN'
        context['es_edicion'] = True
        return context
    
    def form_valid(self, form):
        # Guardar el seguimiento editado
        self.object = form.save()
        
        messages.success(self.request, f'Sesión {self.object.numero_sesion} actualizada exitosamente.')
        
        # Guardar datos en sesión para la vista de cuestionarios
        self.request.session['editar_seguimiento_data'] = {
            'seguimiento_id': self.object.id,
            'form_data': self.request.POST.dict(),  # Convertir QueryDict a dict
            'files_data': self.request.FILES,
        }
        
        # Redirigir a la vista de cuestionarios con modo edición
        return redirect(
            'expedientes:editar_seguimiento_cuestionarios',
            expediente_id=self.expediente.id,
            seguimiento_id=self.object.id
        )
    
    def form_invalid(self, form):
        print("=== ERRORES DEL FORMULARIO DE SEGUIMIENTO (EDICIÓN) ===")
        print(f"Errores: {form.errors}")
        print(f"Datos enviados: {self.request.POST}")
        
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f'Error en {field}: {error}')
        
        return super().form_invalid(form)
    
    def get_success_url(self):
        # Esta URL ya no se usa porque redirigimos manualmente en form_valid
        return reverse('expedientes:expediente_actos', args=[self.expediente.id])
    
class CrearFinalizacionView(LoginRequiredMixin, BaseExpedienteActoView, CreateView):
    model = ConsultaFinalizacion
    form_class = ConsultaFinalizacionForm
    template_name = 'expedientes/actos/finalizacion_form.html'
    
    def dispatch(self, request, *args, **kwargs):
        self.verificar_permiso(request)
        
        self.expediente = get_object_or_404(Expediente, id=kwargs['expediente_id'])
        self.cita = get_object_or_404(Cita, id=kwargs['cita_id'])
        
        es_admin = request.user.tipo_usuario == 'ADMIN'
        fecha_cita = self.cita.fecha.date()
        hoy = timezone.now().date()
        
        # ✅ Solo ADMIN puede crear historias de fechas pasadas
        if not es_admin:
            if fecha_cita != hoy:
                messages.error(request, 'Solo puedes crear la historia clínica el día de la cita.')
                return redirect('expedientes:expediente_actos', expediente_id=self.expediente.id)
        
        if self.cita.estado == 'CANCELADA':
            messages.error(request, 'No puedes crear una historia clínica para una cita cancelada.')
            return redirect('expedientes:expediente_actos', expediente_id=self.expediente.id)
        
        if self.cita.tipo_cita != 'FINALIZACION':
            messages.error(request, 'Esta cita no es de tipo Finalización.')
            return redirect('expedientes:expediente_actos', expediente_id=self.expediente.id)
        
        if not hasattr(self.expediente, 'primera_consulta'):
            messages.error(request, 'Debe existir una Primera Consulta antes de finalizar.')
            return redirect('expedientes:expediente_actos', expediente_id=self.expediente.id)
        
        if self.expediente.seguimientos.count() == 0:
            messages.error(request, 'Debe existir al menos una sesión de seguimiento antes de finalizar.')
            return redirect('expedientes:expediente_actos', expediente_id=self.expediente.id)
        
        if hasattr(self.expediente, 'finalizacion'):
            messages.error(request, 'Este paciente ya tiene una Finalización registrada.')
            return redirect('expedientes:expediente_actos', expediente_id=self.expediente.id)
        
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['expediente'] = self.expediente
        context['paciente'] = self.expediente.paciente
        context['cita'] = self.cita
        context['titulo'] = 'Finalización'
        context['accion'] = 'Crear'
        context['es_admin'] = self.request.user.tipo_usuario == 'ADMIN'
        return context
    
    def form_valid(self, form):
        """Guarda el formulario correctamente"""
        print("=== GUARDANDO FINALIZACION ===")
        
        # Asignar campos faltantes
        form.instance.expediente = self.expediente
        form.instance.profesional = self.request.user
        form.instance.cita = self.cita
        form.instance.fecha_consulta = timezone.now()
        
        # Asegurar que nivel_dolor_final tenga un valor (el slider envía 0 si está vacío)
        if not form.instance.nivel_dolor_final and form.instance.nivel_dolor_final != 0:
            form.instance.nivel_dolor_final = 0
        
        # Guardar la finalización
        self.object = form.save()
        print(f"✅ Finalización guardada con ID: {self.object.id}")
        
        # Actualizar estado de la cita a COMPLETADA
        self.cita.estado = 'COMPLETADA'
        self.cita.save(update_fields=['estado'])
        print(f"✅ Cita {self.cita.id} marcada como COMPLETADA")
        
        # Actualizar estado del expediente a FINALIZADO
        self.expediente.estado = 'FINALIZADO'
        self.expediente.fecha_fin_tratamiento = timezone.now().date()
        self.expediente.save(update_fields=['estado', 'fecha_fin_tratamiento'])
        print(f"✅ Expediente {self.expediente.id} marcado como FINALIZADO")
        
        messages.success(
            self.request, 
            'Finalización creada exitosamente. La cita ha sido marcada como COMPLETADA y el expediente como FINALIZADO.'
        )
        
        success_url = self.get_success_url()
        print(f"✅ Redirigiendo a: {success_url}")
        
        return redirect(success_url)
    
    def form_invalid(self, form):
        """Muestra errores del formulario"""
        print("=== ERRORES DEL FORMULARIO DE FINALIZACION ===")
        print(f"Errores: {form.errors}")
        print(f"Datos enviados: {self.request.POST}")
        
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f'Error en {field}: {error}')
        
        return super().form_invalid(form)
    
    def get_success_url(self):
        return reverse('expedientes:expediente_actos', args=[self.expediente.id])

class EditarFinalizacionView(LoginRequiredMixin, BaseExpedienteActoView, UpdateView):
    model = ConsultaFinalizacion
    form_class = ConsultaFinalizacionForm
    template_name = 'expedientes/actos/finalizacion_form.html'
    
    def dispatch(self, request, *args, **kwargs):
        self.verificar_permiso(request)
        
        self.acto = self.get_object()
        self.expediente = self.acto.expediente
        
        if request.user.tipo_usuario != 'ADMIN':
            tiempo_transcurrido = timezone.now() - self.acto.created_at
            if tiempo_transcurrido > timedelta(hours=1):
                messages.error(request, 'Solo tienes 1 hora después de crear la historia para editarla.')
                return redirect('expedientes:expediente_actos', expediente_id=self.expediente.id)
        
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['expediente'] = self.expediente
        context['paciente'] = self.expediente.paciente
        context['cita'] = self.acto.cita
        context['titulo'] = 'Finalización'
        context['accion'] = 'Editar'
        context['es_admin'] = self.request.user.tipo_usuario == 'ADMIN'
        return context
    
    def form_valid(self, form):
        messages.success(self.request, 'Finalización actualizada exitosamente.')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('expedientes:expediente_actos', args=[self.expediente.id])
    
# ============================================================================
# ELIMINAR ACTOS CLÍNICOS (AJAX)
@require_http_methods(["DELETE"])
@login_required
def eliminar_acto_clinico(request, tipo, id_acto):
    """Endpoint AJAX para eliminar actos clínicos"""
    
    # ✅ Verificar que el usuario tenga permisos básicos (no FISIO)
    if request.user.tipo_usuario not in ['ADMIN', 'MEDIC']:
        return JsonResponse({
            'success': False, 
            'error': 'Solo los administradores y médicos pueden eliminar historias clínicas.'
        }, status=403)
    
    try:
        # Obtener el acto clínico según el tipo
        if tipo == 'primera':
            acto = PrimeraConsulta.objects.get(id=id_acto)
        elif tipo == 'seguimiento':
            acto = ConsultaSegumiento.objects.get(id=id_acto)
        elif tipo == 'finalizacion':
            acto = ConsultaFinalizacion.objects.get(id=id_acto)
        else:
            return JsonResponse({'success': False, 'error': 'Tipo no válido'}, status=400)
        
        # ✅ Si es MEDIC, verificar que fue él quien creó la historia
        if request.user.tipo_usuario == 'MEDIC':
            if acto.profesional != request.user:
                return JsonResponse({
                    'success': False, 
                    'error': 'No puedes eliminar historias que no fueron creadas por ti.'
                }, status=403)
        
        # ✅ Si es ADMIN, puede eliminar cualquier historia sin restricciones
        # (ya pasó la verificación de tipo_usuario)
        
        # Eliminar el acto
        acto.delete()
        
        return JsonResponse({
            'success': True, 
            'message': 'Historia clínica eliminada correctamente.'
        })
        
    except PrimeraConsulta.DoesNotExist:
        return JsonResponse({
            'success': False, 
            'error': 'La Primera Consulta no existe.'
        }, status=404)
    except ConsultaSegumiento.DoesNotExist:
        return JsonResponse({
            'success': False, 
            'error': 'La Consulta de Seguimiento no existe.'
        }, status=404)
    except ConsultaFinalizacion.DoesNotExist:
        return JsonResponse({
            'success': False, 
            'error': 'La Consulta de Finalización no existe.'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False, 
            'error': f'Error al eliminar: {str(e)}'
        }, status=500)

class SeguimientoConCuestionariosView(LoginRequiredMixin, BaseExpedienteActoView, TemplateView):
    """Vista para crear evaluación con modelo 3D y cuestionarios"""
    template_name = 'expedientes/actos/seguimiento_cuestionarios.html'
    
    def dispatch(self, request, *args, **kwargs):
        self.verificar_permiso(request)
        self.expediente = get_object_or_404(Expediente, id=kwargs['expediente_id'])
        self.cita = get_object_or_404(Cita, id=kwargs['cita_id'])
        
        if not hasattr(self.expediente, 'primera_consulta'):
            messages.error(request, 'Debe existir una Primera Consulta antes de crear seguimientos.')
            return redirect('expedientes:expediente_actos', expediente_id=self.expediente.id)
        
        self.seguimiento = ConsultaSegumiento.objects.filter(
            expediente=self.expediente,
            cita=self.cita
        ).order_by('-numero_sesion').first()
        
        if not self.seguimiento:
            messages.error(request, 'No se encontró la sesión de seguimiento.')
            return redirect('expedientes:expediente_actos', expediente_id=self.expediente.id)
        
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'expediente': self.expediente,
            'paciente': self.expediente.paciente,
            'cita': self.cita,
            'seguimiento': self.seguimiento,
            'es_edicion': False,  # <-- Modo creación
        })
        return context
    
    
    def post(self, request, *args, **kwargs):
        """Procesa las respuestas de los cuestionarios y las asocia al seguimiento existente"""
        self.expediente = get_object_or_404(Expediente, id=kwargs['expediente_id'])
        self.cita = get_object_or_404(Cita, id=kwargs['cita_id'])
        
        # Obtener el seguimiento que ya fue creado
        seguimiento = ConsultaSegumiento.objects.filter(
            expediente=self.expediente,
            cita=self.cita
        ).order_by('-numero_sesion').first()
        
        if not seguimiento:
            messages.error(request, 'No se encontró la sesión de seguimiento.')
            return redirect('expedientes:expediente_actos', expediente_id=self.expediente.id)
        
        # Procesar las respuestas de los cuestionarios
        preguntas = PreguntaCuestionario.objects.filter(
            cuestionario__activo=True
        )
        
        respuestas_guardadas = 0
        for pregunta in preguntas:
            respuesta_key = f'pregunta_{pregunta.id}'
            
            if respuesta_key in request.POST:
                valor = request.POST.get(respuesta_key)
                
                # Verificar si ya existe una respuesta para esta pregunta en este seguimiento
                respuesta_existente = RespuestaCuestionario.objects.filter(
                    consulta_seguimiento=seguimiento,
                    pregunta=pregunta
                ).first()
                
                # Crear o actualizar respuesta según tipo de pregunta
                if pregunta.tipo_pregunta in ['ESCALA', 'ESCALA_NUMERICA']:
                    if valor and valor.isdigit():
                        if respuesta_existente:
                            respuesta_existente.respuesta_escala = int(valor)
                            respuesta_existente.save()
                        else:
                            RespuestaCuestionario.objects.create(
                                consulta_seguimiento=seguimiento,
                                pregunta=pregunta,
                                respuesta_escala=int(valor)
                            )
                        respuestas_guardadas += 1
                        
                elif pregunta.tipo_pregunta == 'TEXTO':
                    if valor:
                        if respuesta_existente:
                            respuesta_existente.respuesta_texto = valor
                            respuesta_existente.save()
                        else:
                            RespuestaCuestionario.objects.create(
                                consulta_seguimiento=seguimiento,
                                pregunta=pregunta,
                                respuesta_texto=valor
                            )
                        respuestas_guardadas += 1
                        
                elif pregunta.tipo_pregunta == 'SI_NO':
                    if respuesta_existente:
                        respuesta_existente.respuesta_booleana = (valor == 'si')
                        respuesta_existente.save()
                    else:
                        RespuestaCuestionario.objects.create(
                            consulta_seguimiento=seguimiento,
                            pregunta=pregunta,
                            respuesta_booleana=(valor == 'si')
                        )
                    respuestas_guardadas += 1
                    
                elif pregunta.tipo_pregunta == 'MULTIPLE':
                    if valor:
                        if respuesta_existente:
                            respuesta_existente.respuesta_multiple = valor
                            respuesta_existente.save()
                        else:
                            RespuestaCuestionario.objects.create(
                                consulta_seguimiento=seguimiento,
                                pregunta=pregunta,
                                respuesta_multiple=valor
                            )
                        respuestas_guardadas += 1
        
        # Mensaje de éxito
        messages.success(
            request, 
            f'Sesión {seguimiento.numero_sesion} completada exitosamente. '
            f'Se guardaron {respuestas_guardadas} respuestas de cuestionarios.'
        )
        
        return redirect('expedientes:expediente_actos', expediente_id=self.expediente.id)
    
def api_cuestionarios_por_parte(request):
    """API para cargar cuestionarios según parte del cuerpo seleccionada"""
    parte = request.GET.get('parte', 'hombro')
    
    # Mapeo de partes del cuerpo a tipos de cuestionario
    mapping = {
        'hombro': 'HOMBRO_PECTORAL',
        'espalda': 'ESPALDA',
        'rodilla': 'RODILLA',
        'cuello': 'CUELLO',
        'general': 'GENERAL',
    }
    
    tipo = mapping.get(parte, 'GENERAL')
    
    cuestionario = Cuestionario.objects.filter(
        tipo_cuestionario=tipo,
        activo=True
    ).first()
    
    preguntas = []
    if cuestionario:
        preguntas = cuestionario.preguntas.all().order_by('orden')
    
    # Renderizar HTML
    html = render_to_string('expedientes/actos/_cuestionarios_por_parte.html', {
        'preguntas': preguntas,
        'parte': parte,
    })
    
    return JsonResponse({'html': html, 'parte': parte})


#EDITAR CUESTIONARIOS DE SEGUIMIENTO (NUEVA VISTA)
# expedientes/views.py - Agregar esta nueva vista
# expedientes/views.py - Verificar que esta vista esté completa

class EditarSeguimientoCuestionariosView(LoginRequiredMixin, BaseExpedienteActoView, TemplateView):
    """Vista para editar modelo 3D y cuestionarios de un seguimiento existente"""
    template_name = 'expedientes/actos/seguimiento_cuestionarios.html'  # <-- Mismo template
    
    def dispatch(self, request, *args, **kwargs):
        self.verificar_permiso(request)
        self.expediente = get_object_or_404(Expediente, id=kwargs['expediente_id'])
        self.seguimiento = get_object_or_404(ConsultaSegumiento, id=kwargs['seguimiento_id'])
        
        if self.seguimiento.expediente.id != self.expediente.id:
            messages.error(request, 'El seguimiento no pertenece a este expediente.')
            return redirect('expedientes:expediente_actos', expediente_id=self.expediente.id)
        
        if request.user.tipo_usuario != 'ADMIN':
            tiempo_transcurrido = timezone.now() - self.seguimiento.created_at
            if tiempo_transcurrido > timedelta(hours=1):
                messages.error(request, 'Solo tienes 1 hora después de crear la historia para editarla.')
                return redirect('expedientes:expediente_actos', expediente_id=self.expediente.id)
        
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obtener respuestas existentes
        respuestas_existentes = {}
        respuestas = RespuestaCuestionario.objects.filter(
            consulta_seguimiento=self.seguimiento
        ).select_related('pregunta')
        
        for respuesta in respuestas:
            respuestas_existentes[respuesta.pregunta_id] = respuesta
        
        context.update({
            'expediente': self.expediente,
            'paciente': self.expediente.paciente,
            'seguimiento': self.seguimiento,
            'cita': self.seguimiento.cita,
            'respuestas_existentes': respuestas_existentes,
            'es_edicion': True,  # <-- Modo edición
        })
        return context
    
    def post(self, request, *args, **kwargs):
        """Procesa y actualiza las respuestas de los cuestionarios"""
        self.expediente = get_object_or_404(Expediente, id=kwargs['expediente_id'])
        self.seguimiento = get_object_or_404(ConsultaSegumiento, id=kwargs['seguimiento_id'])
        
        # Procesar las respuestas de los cuestionarios
        preguntas = PreguntaCuestionario.objects.filter(
            cuestionario__activo=True
        )
        
        respuestas_actualizadas = 0
        respuestas_creadas = 0
        
        for pregunta in preguntas:
            respuesta_key = f'pregunta_{pregunta.id}'
            
            if respuesta_key in request.POST:
                valor = request.POST.get(respuesta_key)
                
                # Buscar respuesta existente
                respuesta_existente = RespuestaCuestionario.objects.filter(
                    consulta_seguimiento=self.seguimiento,
                    pregunta=pregunta
                ).first()
                
                # Crear o actualizar respuesta según tipo de pregunta
                if pregunta.tipo_pregunta in ['ESCALA', 'ESCALA_NUMERICA']:
                    if valor and valor.isdigit():
                        if respuesta_existente:
                            respuesta_existente.respuesta_escala = int(valor)
                            respuesta_existente.save()
                            respuestas_actualizadas += 1
                        else:
                            RespuestaCuestionario.objects.create(
                                consulta_seguimiento=self.seguimiento,
                                pregunta=pregunta,
                                respuesta_escala=int(valor)
                            )
                            respuestas_creadas += 1
                        
                elif pregunta.tipo_pregunta == 'TEXTO':
                    if valor:
                        if respuesta_existente:
                            respuesta_existente.respuesta_texto = valor
                            respuesta_existente.save()
                            respuestas_actualizadas += 1
                        else:
                            RespuestaCuestionario.objects.create(
                                consulta_seguimiento=self.seguimiento,
                                pregunta=pregunta,
                                respuesta_texto=valor
                            )
                            respuestas_creadas += 1
                        
                elif pregunta.tipo_pregunta == 'SI_NO':
                    if respuesta_existente:
                        respuesta_existente.respuesta_booleana = (valor == 'si')
                        respuesta_existente.save()
                        respuestas_actualizadas += 1
                    else:
                        RespuestaCuestionario.objects.create(
                            consulta_seguimiento=self.seguimiento,
                            pregunta=pregunta,
                            respuesta_booleana=(valor == 'si')
                        )
                        respuestas_creadas += 1
                        
                elif pregunta.tipo_pregunta == 'MULTIPLE':
                    if valor:
                        if respuesta_existente:
                            respuesta_existente.respuesta_multiple = valor
                            respuesta_existente.save()
                            respuestas_actualizadas += 1
                        else:
                            RespuestaCuestionario.objects.create(
                                consulta_seguimiento=self.seguimiento,
                                pregunta=pregunta,
                                respuesta_multiple=valor
                            )
                            respuestas_creadas += 1
        
        # Mensaje de éxito
        messages.success(
            request, 
            f'Sesión {self.seguimiento.numero_sesion} actualizada exitosamente. '
            f'Respuestas: {respuestas_creadas} creadas, {respuestas_actualizadas} actualizadas.'
        )
        
        return redirect('expedientes:expediente_actos', expediente_id=self.expediente.id)

# expedientes/views.py - Modificar api_cuestionarios_por_parte
def api_cuestionarios_por_parte(request):
    """API para cargar cuestionarios según parte del cuerpo seleccionada"""
    parte = request.GET.get('parte', 'hombro')
    es_edicion = request.GET.get('edicion', 'false') == 'true'
    seguimiento_id = request.GET.get('seguimiento_id')
    
    from cuestionarios.models import Cuestionario, PreguntaCuestionario, RespuestaCuestionario
    
    mapping = {
        'hombro': 'HOMBRO_PECTORAL',
        'espalda': 'ESPALDA',
        'rodilla': 'RODILLA',
        'cuello': 'CUELLO',
        'general': 'GENERAL',
    }
    
    tipo = mapping.get(parte, 'GENERAL')
    
    cuestionario = Cuestionario.objects.filter(
        tipo_cuestionario=tipo,
        activo=True
    ).first()
    
    preguntas = []
    respuestas_existentes = {}
    
    if cuestionario:
        preguntas = cuestionario.preguntas.all().order_by('orden')
        
        if es_edicion and seguimiento_id:
            respuestas = RespuestaCuestionario.objects.filter(
                consulta_seguimiento_id=seguimiento_id,
                pregunta__in=preguntas
            ).select_related('pregunta')
            
            for respuesta in respuestas:
                respuestas_existentes[respuesta.pregunta_id] = respuesta
    
    html = render_to_string('expedientes/actos/_cuestionarios_por_parte.html', {
        'preguntas': preguntas,
        'parte': parte,
        'es_edicion': es_edicion,
        'respuestas_existentes': respuestas_existentes,
    })
    
    return JsonResponse({'html': html, 'parte': parte})


class VisualizarModelo3DView(LoginRequiredMixin, TemplateView):
    """Vista para visualizar el modelo 3D del cuerpo humano"""
    template_name = 'modelo_3d/visualizar_modelo.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obtener el paciente si se pasa un ID
        paciente_id = self.request.GET.get('paciente_id')
        if paciente_id:
            from paciente.models import Patient
            context['paciente'] = get_object_or_404(Patient, id=paciente_id)
        else:
            context['paciente'] = None
        
        return context
