# cuestionarios/views.py
from django.db import models
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy, reverse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.http import JsonResponse
from .models import Cuestionario, PreguntaCuestionario, RespuestaCuestionario, AnalisisPredictivoEscala, EvolucionPaciente
from .forms import CuestionarioForm, PreguntaCuestionarioForm, RespuestaCuestionarioFormSet
from django.db.models import Q
from django.core.paginator import Paginator
from paciente.models import Patient
from expedientes.models import Expediente, ConsultaSegumiento
    # cuestionarios/views.py - Agregar al final del archivo

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json


class CuestionarioListView(LoginRequiredMixin, ListView):
    """Lista de cuestionarios disponibles"""
    model = Cuestionario
    template_name = 'cuestionarios/cuestionario_list.html'
    context_object_name = 'cuestionarios'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_superuser:
            queryset = queryset.filter(activo=True)
        
        # Filtro por tipo
        tipo = self.request.GET.get('tipo')
        if tipo:
            queryset = queryset.filter(tipo_cuestionario=tipo)
        
        # Búsqueda
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(nombre__icontains=search) | Q(descripcion__icontains=search)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tipos'] = Cuestionario.TIPO_CUESTIONARIO
        context['total_cuestionarios'] = self.get_queryset().count()
        return context

class CuestionarioDetailView(LoginRequiredMixin, DetailView):
    """Detalle de un cuestionario con sus preguntas"""
    model = Cuestionario
    template_name = 'cuestionarios/cuestionario_detail.html'
    context_object_name = 'cuestionario'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['url_boton'] = reverse('gestionar_usuario')
        context['preguntas'] = self.object.preguntas.all().order_by('orden')
        context['total_preguntas'] = context['preguntas'].count()
        context['tipos_pregunta'] = PreguntaCuestionario.TIPO_PREGUNTA
        return context

class CuestionarioCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """Crear nuevo cuestionario"""
    model = Cuestionario
    form_class = CuestionarioForm
    template_name = 'cuestionarios/cuestionario_form.html'
    permission_required = 'cuestionarios.add_cuestionario'
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, f'¡Cuestionario "{form.instance.nombre}" creado exitosamente!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('cuestionarios:detail', kwargs={'pk': self.object.pk})

class CuestionarioUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """Editar cuestionario"""
    model = Cuestionario
    form_class = CuestionarioForm
    template_name = 'cuestionarios/cuestionario_form.html'
    permission_required = 'cuestionarios.change_cuestionario'
    
    def form_valid(self, form):
        messages.success(self.request, f'¡Cuestionario "{form.instance.nombre}" actualizado exitosamente!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('cuestionarios:detail', kwargs={'pk': self.object.pk})

class CuestionarioDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """Eliminar cuestionario"""
    model = Cuestionario
    template_name = 'cuestionarios/cuestionario_confirm_delete.html'
    permission_required = 'cuestionarios.delete_cuestionario'
    success_url = reverse_lazy('cuestionarios:list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Cuestionario eliminado exitosamente.')
        return super().delete(request, *args, **kwargs)

class PreguntaCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """Crear nueva pregunta en un cuestionario"""
    model = PreguntaCuestionario
    form_class = PreguntaCuestionarioForm
    template_name = 'cuestionarios/pregunta_form.html'
    permission_required = 'cuestionarios.add_preguntacuestionario'
    
    def dispatch(self, request, *args, **kwargs):
        self.cuestionario = get_object_or_404(Cuestionario, pk=kwargs['cuestionario_pk'])
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cuestionario'] = self.cuestionario
        return context
    
    def form_valid(self, form):
        form.instance.cuestionario = self.cuestionario
        # Asignar orden automáticamente
        if not form.instance.orden:
            ultimo_orden = self.cuestionario.preguntas.aggregate(models.Max('orden'))['orden__max'] or 0
            form.instance.orden = ultimo_orden + 1
        
        messages.success(self.request, 'Pregunta agregada exitosamente.')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('cuestionarios:detail', kwargs={'pk': self.cuestionario.pk})

class PreguntaUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """Editar pregunta"""
    model = PreguntaCuestionario
    form_class = PreguntaCuestionarioForm
    template_name = 'cuestionarios/pregunta_form.html'
    permission_required = 'cuestionarios.change_preguntacuestionario'
    
    def get_success_url(self):
        return reverse('cuestionarios:detail', kwargs={'pk': self.object.cuestionario.pk})

class PreguntaDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """Eliminar pregunta"""
    model = PreguntaCuestionario
    permission_required = 'cuestionarios.delete_preguntacuestionario'
    
    def get_success_url(self):
        return reverse('cuestionarios:detail', kwargs={'pk': self.object.cuestionario.pk})

class EvolucionGraficoView(LoginRequiredMixin, TemplateView):
    """Vista para mostrar gráficos de evolución"""
    template_name = 'cuestionarios/evolucion_grafico.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        expediente = get_object_or_404(Expediente, pk=kwargs['expediente_pk'])
        
        # Obtener evoluciones del paciente
        evoluciones = EvolucionPaciente.objects.filter(expediente=expediente)
        
        # Obtener datos para gráficos
        datos_graficos = []
        for evol in evoluciones:
            datos_graficos.append({
                'id': evol.id,
                'titulo': evol.tipo_evaluacion,
                'datos': evol.evolucion_historica,
                'tendencia': evol.tendencia_general,
                'mejoria': evol.porcentaje_mejoria,
                'mejor_valor': evol.mejor_valor,
                'peor_valor': evol.peor_valor,
                'promedio': round(evol.promedio, 2)
            })
        
        # Obtener predicciones
        predicciones = AnalisisPredictivoEscala.objects.filter(
            consulta_seguimiento__expediente=expediente,
            prediccion_siguiente__isnull=False
        ).select_related('pregunta')
        
        context['expediente'] = expediente
        context['datos_graficos'] = datos_graficos
        context['predicciones'] = predicciones
        context['total_evoluciones'] = evoluciones.count()
        
        return context

def api_evolucion_data(request, expediente_pk, pregunta_pk):
    """API para obtener datos de evolución en JSON"""
    expediente = get_object_or_404(Expediente, pk=expediente_pk)
    pregunta = get_object_or_404(PreguntaCuestionario, pk=pregunta_pk)
    
    analisis = AnalisisPredictivoEscala.objects.filter(
        consulta_seguimiento__expediente=expediente,
        pregunta=pregunta
    ).order_by('sesion_numero')
    
    data = {
        'pregunta': pregunta.texto_pregunta,
        'datos': [
            {
                'sesion': a.sesion_numero,
                'fecha': a.fecha_consulta.strftime('%Y-%m-%d'),
                'valor': a.valor_escala,
                'prediccion': a.prediccion_siguiente
            }
            for a in analisis
        ]
    }
    
    return JsonResponse(data)



@csrf_exempt
def api_agregar_pregunta_cuestionario(request):
    """API para agregar una nueva pregunta personalizada"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método no permitido'})
    
    try:
        data = json.loads(request.body)
        
        from .models import Cuestionario, PreguntaCuestionario
        
        parte = data.get('parte')
        mapping = {
            'hombro': 'HOMBRO_PECTORAL',
            'espalda': 'ESPALDA',
            'rodilla': 'RODILLA',
            'cuello': 'CUELLO',
            'general': 'GENERAL',
        }
        tipo = mapping.get(parte, 'GENERAL')
        
        # Obtener o crear cuestionario para este tipo
        cuestionario, created = Cuestionario.objects.get_or_create(
            tipo_cuestionario=tipo,
            defaults={
                'nombre': f'Evaluación de {parte.capitalize()}',
                'descripcion': f'Cuestionario personalizado para {parte}',
                'activo': True,
                'created_by': request.user if request.user.is_authenticated else None
            }
        )
        
        # Crear la pregunta
        pregunta = PreguntaCuestionario.objects.create(
            cuestionario=cuestionario,
            texto_pregunta=data.get('texto_pregunta'),
            tipo_pregunta=data.get('tipo_pregunta'),
            obligatorio=data.get('obligatorio', True),
            orden=data.get('orden', 0),
            escala_min=data.get('escala_min', 0),
            escala_max=data.get('escala_max', 10),
            etiqueta_min=data.get('etiqueta_min', 'Sin dolor'),
            etiqueta_max=data.get('etiqueta_max', 'Máximo dolor'),
            opciones=data.get('opciones', []),
            es_indicador_clave=True
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Pregunta agregada exitosamente',
            'pregunta_id': pregunta.id
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@csrf_exempt
def api_editar_pregunta_cuestionario(request):
    """API para editar una pregunta existente"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método no permitido'})
    
    try:
        data = json.loads(request.body)
        
        from .models import PreguntaCuestionario
        
        pregunta = get_object_or_404(PreguntaCuestionario, id=data.get('pregunta_id'))
        
        # Actualizar campos
        pregunta.texto_pregunta = data.get('texto_pregunta', pregunta.texto_pregunta)
        pregunta.tipo_pregunta = data.get('tipo_pregunta', pregunta.tipo_pregunta)
        pregunta.obligatorio = data.get('obligatorio', pregunta.obligatorio)
        pregunta.orden = data.get('orden', pregunta.orden)
        
        if data.get('tipo_pregunta') in ['ESCALA', 'ESCALA_NUMERICA']:
            pregunta.escala_min = data.get('escala_min', 0)
            pregunta.escala_max = data.get('escala_max', 10)
            pregunta.etiqueta_min = data.get('etiqueta_min', 'Sin dolor')
            pregunta.etiqueta_max = data.get('etiqueta_max', 'Máximo dolor')
        
        if data.get('tipo_pregunta') == 'MULTIPLE':
            pregunta.opciones = data.get('opciones', [])
        
        pregunta.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Pregunta actualizada exitosamente'
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@csrf_exempt
def api_eliminar_pregunta_cuestionario(request):
    """API para eliminar una pregunta"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método no permitido'})
    
    try:
        data = json.loads(request.body)
        
        from .models import PreguntaCuestionario
        
        pregunta = get_object_or_404(PreguntaCuestionario, id=data.get('pregunta_id'))
        pregunta.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Pregunta eliminada exitosamente'
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


# cuestionarios/views.py - Agregar al final del archivo



class BuscadorPacientesView(LoginRequiredMixin, ListView):
    """Vista para buscar pacientes por expediente y ver su historial"""
    model = Patient
    template_name = 'cuestionarios/buscador_pacientes.html'
    context_object_name = 'pacientes'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = Patient.objects.all()
        search = self.request.GET.get('search', '')
        
        if search:
            queryset = queryset.filter(
                Q(expediente__numero_expediente__icontains=search) |
                Q(nombres__icontains=search) |
                Q(apellidos__icontains=search) |
                Q(cedula__icontains=search)
            )
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        return context


class VerHistorialPacienteView(LoginRequiredMixin, DetailView):
    """Vista para ver el historial completo de respuestas de un paciente"""
    model = Patient
    template_name = 'cuestionarios/historial_paciente.html'
    context_object_name = 'paciente'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        paciente = self.object
        
        # Obtener el expediente
        expediente = getattr(paciente, 'expediente', None)
        
        if expediente:
            # Obtener todas las sesiones de seguimiento
            sesiones = ConsultaSegumiento.objects.filter(
                expediente=expediente
            ).order_by('-fecha_consulta')
            
            # Para cada sesión, obtener sus respuestas
            sesiones_con_respuestas = []
            for sesion in sesiones:
                respuestas = RespuestaCuestionario.objects.filter(
                    consulta_seguimiento=sesion
                ).select_related('pregunta__cuestionario')
                
                # Calcular promedio de escala
                valores_escala = [r.respuesta_escala for r in respuestas if r.respuesta_escala is not None]
                promedio = round(sum(valores_escala) / len(valores_escala), 1) if valores_escala else None
                
                # Obtener parte del cuerpo
                parte = 'General'
                if respuestas.exists():
                    primera_pregunta = respuestas.first().pregunta
                    if primera_pregunta and primera_pregunta.cuestionario:
                        parte = primera_pregunta.cuestionario.get_tipo_cuestionario_display()
                
                sesiones_con_respuestas.append({
                    'sesion': sesion,
                    'respuestas': respuestas,
                    'promedio_dolor': promedio,
                    'parte': parte,
                })
            
            context['sesiones'] = sesiones_con_respuestas
            context['expediente'] = expediente
            context['total_sesiones'] = sesiones.count()
        else:
            context['sesiones'] = []
            context['expediente'] = None
            context['total_sesiones'] = 0
        
        return context