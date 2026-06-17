# cuestionarios/views.py
from django.db import models
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy, reverse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Avg, Count, Q
from django.utils import timezone
from .models import Cuestionario, PreguntaCuestionario, RespuestaCuestionario, AnalisisPredictivoEscala, EvolucionPaciente
from .forms import CuestionarioForm, PreguntaCuestionarioForm, RespuestaCuestionarioFormSet
from .services import AnalisisPredictivoService

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

def responder_cuestionario(request, cuestionario_pk, consulta_pk):
    """Vista para responder un cuestionario en una consulta específica"""
    cuestionario = get_object_or_404(Cuestionario, pk=cuestionario_pk, activo=True)
    from expedientes.models import ConsultaSegumiento  # Importar aquí para evitar circular
    consulta = get_object_or_404(ConsultaSegumiento, pk=consulta_pk)
    
    # Verificar si ya se respondió este cuestionario para esta consulta
    respuestas_existentes = RespuestaCuestionario.objects.filter(
        consulta_seguimiento=consulta,
        pregunta__cuestionario=cuestionario
    )
    
    if respuestas_existentes.exists() and request.method != 'POST':
        messages.warning(request, 'Este cuestionario ya ha sido respondido para esta consulta.')
        return redirect('expedientes:consulta_detail', pk=consulta_pk)
    
    if request.method == 'POST':
        preguntas = cuestionario.preguntas.all().order_by('orden')
        service = AnalisisPredictivoService()
        
        for pregunta in preguntas:
            respuesta_key = f'pregunta_{pregunta.id}'
            
            if respuesta_key in request.POST:
                # Procesar según tipo de pregunta
                if pregunta.tipo_pregunta in ['ESCALA', 'ESCALA_NUMERICA']:
                    valor = request.POST.get(respuesta_key)
                    if valor and valor.isdigit():
                        respuesta_escala = int(valor)
                        RespuestaCuestionario.objects.update_or_create(
                            consulta_seguimiento=consulta,
                            pregunta=pregunta,
                            defaults={
                                'respuesta_escala': respuesta_escala,
                                'fecha_respuesta': timezone.now()
                            }
                        )
                        # Sincronizar con análisis predictivo
                        respuesta = RespuestaCuestionario.objects.get(
                            consulta_seguimiento=consulta, 
                            pregunta=pregunta
                        )
                        service.sincronizar_respuesta_escala(respuesta)
                
                elif pregunta.tipo_pregunta == 'TEXTO':
                    valor = request.POST.get(respuesta_key, '')
                    RespuestaCuestionario.objects.update_or_create(
                        consulta_seguimiento=consulta,
                        pregunta=pregunta,
                        defaults={
                            'respuesta_texto': valor,
                            'fecha_respuesta': timezone.now()
                        }
                    )
                
                elif pregunta.tipo_pregunta == 'SI_NO':
                    valor = request.POST.get(respuesta_key) == 'si'
                    RespuestaCuestionario.objects.update_or_create(
                        consulta_seguimiento=consulta,
                        pregunta=pregunta,
                        defaults={
                            'respuesta_booleana': valor,
                            'fecha_respuesta': timezone.now()
                        }
                    )
                
                elif pregunta.tipo_pregunta == 'MULTIPLE':
                    valor = request.POST.get(respuesta_key, '')
                    RespuestaCuestionario.objects.update_or_create(
                        consulta_seguimiento=consulta,
                        pregunta=pregunta,
                        defaults={
                            'respuesta_multiple': valor,
                            'fecha_respuesta': timezone.now()
                        }
                    )
        
        messages.success(request, f'¡Cuestionario "{cuestionario.nombre}" guardado exitosamente!')
        return redirect('expedientes:consulta_detail', pk=consulta_pk)
    
    # GET: Mostrar formulario
    preguntas = cuestionario.preguntas.all().order_by('orden')
    
    context = {
        'cuestionario': cuestionario,
        'consulta': consulta,
        'preguntas': preguntas,
    }
    return render(request, 'cuestionarios/responder_cuestionario.html', context)

class EvolucionGraficoView(LoginRequiredMixin, TemplateView):
    """Vista para mostrar gráficos de evolución"""
    template_name = 'cuestionarios/evolucion_grafico.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from expedientes.models import Expediente
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
    from expedientes.models import Expediente
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