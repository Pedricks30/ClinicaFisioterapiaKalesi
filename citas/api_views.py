from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from datetime import datetime, timedelta
from django.utils import timezone  # ← IMPORTANTE: usar django.utils.timezone
from django.db import models
from paciente.models import Patient
from users.models import CustomUser, Specialties
from medical.models import Medico
from physiotherapist.models import Fisioterapeuta
from horario.models import Horario
from .models import Cita


@require_GET
@login_required
def filtrar_profesionales_por_especialidad(request):
    """
    Retorna JSON con profesionales que tienen la especialidad seleccionada.
    """
    especialidad_id = request.GET.get('especialidad_id')
    if not especialidad_id:
        return JsonResponse({'profesionales': []})
    
    profesionales = []
    
    # Obtener médicos con esta especialidad
    medicos = Medico.objects.filter(specialties_id=especialidad_id).select_related('user', 'specialties')
    for medico in medicos:
        if medico.user.is_active:
            profesionales.append({
                'id': medico.user.id,
                'nombre': medico.user.get_full_name(),
                'tipo': 'Médico',
                'especialidad': medico.specialties.specialties if medico.specialties else '',
                'horarios': _get_horarios_resumen(medico.user)
            })
    
    # Obtener fisioterapeutas con esta especialidad
    fisioterapeutas = Fisioterapeuta.objects.filter(specialties_id=especialidad_id).select_related('user', 'specialties')
    for fisio in fisioterapeutas:
        if fisio.user.is_active:
            profesionales.append({
                'id': fisio.user.id,
                'nombre': fisio.user.get_full_name(),
                'tipo': 'Fisioterapeuta',
                'especialidad': fisio.specialties.specialties if fisio.specialties else '',
                'horarios': _get_horarios_resumen(fisio.user)
            })
    
    # Ordenar por nombre
    profesionales.sort(key=lambda x: x['nombre'])
    
    return JsonResponse({'profesionales': profesionales})


@require_GET
@login_required
def get_horarios_profesional(request, profesional_id):
    """
    Retorna los horarios de un profesional para mostrarlos en la tabla.
    """
    horarios = Horario.objects.filter(
        profesional_id=profesional_id,
        disponible=True
    ).order_by('hora_inicio')
    
    data = []
    for h in horarios:
        dias = h.get_dias_display()
        # Si dias es una lista, convertir a string
        if isinstance(dias, list):
            dias = ', '.join(dias)
        
        data.append({
            'id': h.id,
            'dias': dias,
            'hora_inicio': h.hora_inicio.strftime('%H:%M'),
            'hora_fin': h.hora_fin.strftime('%H:%M'),
        })
    
    return JsonResponse({'horarios': data})

@require_GET
@login_required
def get_horas_disponibles(request, profesional_id, fecha_str):
    """
    Retorna las horas disponibles de un profesional para una fecha específica.
    """
    try:
        fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
    except ValueError:
        return JsonResponse({'error': 'Formato de fecha inválido'}, status=400)
    
    profesional = get_object_or_404(CustomUser, pk=profesional_id)
    
    # Obtener el ID de la cita que se está editando
    cita_editando_id = request.GET.get('cita_id', None)
    
    # Mapear día de la semana
    weekday_map = {0: 'LUN', 1: 'MAR', 2: 'MIE', 3: 'JUE', 4: 'VIE', 5: 'SAB', 6: 'DOM'}
    dia_semana = weekday_map[fecha.weekday()]
    
    # Horarios del profesional para ese día
    horarios = Horario.objects.filter(
        profesional=profesional,
        dias_semana__contains=dia_semana,
        disponible=True
    ).order_by('hora_inicio')
    
    # Citas existentes para ese día
    citas_existentes = Cita.objects.filter(
        profesional=profesional,
        fecha__date=fecha,
        estado__in=['PENDIENTE', 'CONFIRMADA', 'EN_PROCESO', 'NO_ASISTIO']
    )
    
    # Excluir la cita que se está editando
    if cita_editando_id:
        citas_existentes = citas_existentes.exclude(id=cita_editando_id)
    
    # Obtener la hora de la cita que se está editando (si existe)
    hora_cita_editando = None
    if cita_editando_id:
        try:
            cita_editando = Cita.objects.get(id=cita_editando_id)
            hora_cita_editando = cita_editando.fecha.strftime('%H:%M')
        except Cita.DoesNotExist:
            pass
    
    slots_disponibles = []
    for horario in horarios:
        inicio = datetime.combine(fecha, horario.hora_inicio)
        fin = datetime.combine(fecha, horario.hora_fin)
        
        current = inicio
        
        while current + timedelta(minutes=30) <= fin:
            slot_fin = current + timedelta(minutes=30)
            
            # Convertir a timezone-aware
            current_aware = timezone.make_aware(current) if timezone.is_naive(current) else current
            slot_fin_aware = timezone.make_aware(slot_fin) if timezone.is_naive(slot_fin) else slot_fin
            
            # Verificar si este slot es la hora de la cita que se está editando
            es_hora_actual = (hora_cita_editando == current.strftime('%H:%M'))
            
            disponible = True
            for cita in citas_existentes:
                cita_fin = cita.fecha + timedelta(minutes=cita.duracion)
                if (current_aware < cita_fin) and (slot_fin_aware > cita.fecha):
                    disponible = False
                    break
            
            # Si es la hora actual de la cita, siempre incluirla aunque no esté disponible
            if es_hora_actual or disponible:
                slots_disponibles.append({
                    'hora': current.strftime('%H:%M'),
                    'hora_fin': slot_fin.strftime('%H:%M'),
                    'datetime': current.isoformat(),
                    'es_hora_actual': es_hora_actual,  # Marcar si es la hora actual
                    'disponible': disponible
                })
            
            current += timedelta(minutes=30)
    
    return JsonResponse({'slots': slots_disponibles})

@require_GET
@login_required
def get_eventos_calendario(request):
    """
    Retorna eventos para FullCalendar en formato JSON.
    """
    profesional_id = request.GET.get('profesional_id')
    
    citas = Cita.objects.filter(
        estado__in=['PENDIENTE', 'CONFIRMADA', 'EN_PROCESO', 'COMPLETADA']
    ).select_related('paciente', 'profesional')
    
    if profesional_id:
        citas = citas.filter(profesional_id=profesional_id)
    
    user = request.user
    if user.tipo_usuario == 'MEDIC' or user.tipo_usuario == 'FISIO':
        citas = citas.filter(profesional=user)
    elif user.tipo_usuario == 'ADMIN' or user.tipo_usuario == 'RECEP':
        pass
    else:
        citas = citas.none()
    
    events = []
    for cita in citas:
        paciente_text = f"{cita.paciente.get_full_name()} - {cita.paciente.tipo_documento} ({cita.paciente.documento_identidad})"
        
        # 🔴 Usar formato local sin zona horaria
        start_local = cita.fecha.strftime('%Y-%m-%dT%H:%M:%S')
        end_local = (cita.fecha + timedelta(minutes=cita.duracion)).strftime('%Y-%m-%dT%H:%M:%S')
        
        events.append({
            'id': cita.id,
            'title': f"{cita.paciente.apellidos}, {cita.paciente.nombres[:1]}. - {cita.motivo[:30]}",
            'start': start_local,
            'end': end_local,
            'backgroundColor': cita.color if cita.color else "#007BFF",
            'borderColor': "#039425FF",
            'extendedProps': {
                'paciente_id': cita.paciente.id,
                'paciente_nombre': cita.paciente.get_full_name(),
                'paciente_text': paciente_text,
                'profesional_id': cita.profesional.id,
                'profesional_nombre': cita.profesional.get_full_name(),
                'motivo': cita.motivo,
                'estado': cita.estado,
                'duracion': cita.duracion,
                'tipo_cita': cita.tipo_cita,
                'hora_cita': cita.fecha.strftime('%H:%M'),  # Nueva propiedad
            }
        })
    
    return JsonResponse(events, safe=False)

@require_GET
@login_required
def buscar_citas(request):
    """
    Endpoint para búsqueda AJAX de citas (para la tabla de búsqueda general).
    """
    q = request.GET.get('q', '').strip()
    estado = request.GET.get('estado', '')
    fecha_desde = request.GET.get('fecha_desde', '')
    fecha_hasta = request.GET.get('fecha_hasta', '')
    
    queryset = Cita.objects.select_related('paciente', 'profesional')
    
    # Filtros según tipo de usuario
    user = request.user
    if user.tipo_usuario == 'MEDIC' or user.tipo_usuario == 'FISIO':
        queryset = queryset.filter(profesional=user)
    
    if q:
        queryset = queryset.filter(
            models.Q(paciente__nombres__icontains=q) |
            models.Q(paciente__apellidos__icontains=q) |
            models.Q(paciente__documento_identidad__icontains=q) |
            models.Q(profesional__first_name__icontains=q) |
            models.Q(profesional__last_name__icontains=q) |
            models.Q(motivo__icontains=q)
        )
    
    if estado:
        queryset = queryset.filter(estado=estado)
    
    if fecha_desde:
        queryset = queryset.filter(fecha__date__gte=fecha_desde)
    if fecha_hasta:
        queryset = queryset.filter(fecha__date__lte=fecha_hasta)
    
    citas = queryset.order_by('-fecha')[:50]
    
    data = []
    for c in citas:
        data.append({
            'id': c.id,
            'paciente': c.paciente.get_full_name(),
            'profesional': c.profesional.get_full_name(),
            'fecha': c.fecha.strftime('%d/%m/%Y %H:%M'),
            'motivo': c.motivo[:50],
            'estado': c.get_estado_display(),
            'estado_class': _get_estado_class(c.estado),
            'duracion': c.duracion,
            'tipo_cita': c.get_tipo_cita_display(),
        })
    
    return JsonResponse({'citas': data, 'total': queryset.count()})


# -------------------------------------------------------------------------
# FUNCIONES AUXILIARES
# -------------------------------------------------------------------------

def _get_horarios_resumen(profesional):
    """Resumen de horarios para mostrar en el selector de profesional"""
    try:
        horarios = Horario.objects.filter(profesional=profesional, disponible=True)
        if horarios.exists():
            h = horarios.first()
            dias = h.get_dias_display()
            if isinstance(dias, list):
                dias = ', '.join(dias[:3])  # Mostrar solo primeros 3 días
                if len(h.get_dias_display()) > 3:
                    dias += '...'
            return f"{dias} | {h.hora_inicio.strftime('%H:%M')}-{h.hora_fin.strftime('%H:%M')}"
        return "Sin horario asignado"
    except Exception as e:
        print(f"Error en _get_horarios_resumen: {e}")
        return "Horario no disponible"


def _get_estado_class(estado):
    clases = {
        'PENDIENTE': 'warning',
        'CONFIRMADA': 'success',
        'EN_PROCESO': 'info',
        'COMPLETADA': 'primary',
        'CANCELADA': 'danger',
        'REPROGRAMADA': 'secondary',
        'NO_ASISTIO': 'dark',
    }
    return clases.get(estado, 'secondary')

@require_GET
@login_required
def verificar_puede_finalizar(request):
    """
    Verifica si un paciente puede ser finalizado (tiene al menos una sesión de seguimiento)
    """
    paciente_id = request.GET.get('paciente_id')
    profesional_id = request.GET.get('profesional_id')
    
    if not paciente_id or not profesional_id:
        return JsonResponse({'puede_finalizar': False, 'error': 'Faltan parámetros'})
    
    try:
        paciente = Patient.objects.get(pk=paciente_id)
        
        # ✅ Verificar que NO tenga citas pendientes (EXCLUYENDO NO_ASISTIO)
        tiene_citas_pendientes = Cita.objects.filter(
            paciente_id=paciente_id,
            profesional_id=profesional_id,
            estado__in=['PENDIENTE', 'CONFIRMADA', 'EN_PROCESO']  # 👈 Solo estos estados
        ).exists()
        
        # Verificar si tiene al menos una cita de seguimiento completada
        tiene_seguimiento = Cita.objects.filter(
            paciente_id=paciente_id,
            profesional_id=profesional_id,
            tipo_cita='SEGUIMIENTO',
            estado='COMPLETADA'
        ).exists()
        
        # Verificar si ya tiene finalización
        tiene_finalizacion = Cita.objects.filter(
            paciente_id=paciente_id,
            profesional_id=profesional_id,
            tipo_cita='FINALIZACION',
            estado__in=['PENDIENTE', 'CONFIRMADA', 'COMPLETADA']
        ).exists()
        
        # Verificar que tenga primera consulta COMPLETADA
        tiene_primera_consulta = Cita.objects.filter(
            paciente_id=paciente_id,
            profesional_id=profesional_id,
            tipo_cita='PRIMERA_CONSULTA',
            estado='COMPLETADA'
        ).exists()
        
        # ✅ CORREGIDO: También verificar que NO tenga una finalización ya creada
        puede_finalizar = (
            tiene_primera_consulta and 
            tiene_seguimiento and 
            not tiene_finalizacion and 
            not tiene_citas_pendientes
        )
        
        return JsonResponse({
            'puede_finalizar': puede_finalizar,
            'tiene_primera_consulta': tiene_primera_consulta,
            'tiene_seguimiento': tiene_seguimiento,
            'tiene_finalizacion': tiene_finalizacion,
            'tiene_citas_pendientes': tiene_citas_pendientes
        })
    except Patient.DoesNotExist:
        return JsonResponse({'puede_finalizar': False, 'error': 'Paciente no encontrado'})

@require_GET
@login_required
def verificar_estado_paciente(request):
    """
    Verifica si el paciente tiene citas pendientes y su estado general
    """
    paciente_id = request.GET.get('paciente_id')
    profesional_id = request.GET.get('profesional_id')
    
    if not paciente_id or not profesional_id:
        return JsonResponse({'error': 'Faltan parámetros'}, status=400)
    
    paciente = get_object_or_404(Patient, pk=paciente_id)
    
    # ✅ EXCLUIR NO_ASISTIO y CANCELADA de las citas pendientes
    citas_pendientes = Cita.objects.filter(
        paciente=paciente,
        profesional_id=profesional_id,
        estado__in=['PENDIENTE', 'CONFIRMADA', 'EN_PROCESO']  # 👈 Solo estos estados
    )
    
    # Verificar citas completadas
    citas_completadas = Cita.objects.filter(
        paciente=paciente,
        profesional_id=profesional_id,
        estado='COMPLETADA'
    )
    
    tiene_primera_consulta = citas_completadas.filter(tipo_cita='PRIMERA_CONSULTA').exists()
    tiene_finalizacion = citas_completadas.filter(tipo_cita='FINALIZACION').exists()
    sesiones_seguimiento = citas_completadas.filter(tipo_cita='SEGUIMIENTO').count()
    
    return JsonResponse({
        'tiene_citas_pendientes': citas_pendientes.exists(),
        'cantidad_citas_pendientes': citas_pendientes.count(),
        'citas_pendientes': [
            {
                'id': c.id,
                'fecha': c.fecha.strftime('%d/%m/%Y %H:%M'),
                'tipo': c.get_tipo_cita_display(),
                'estado': c.get_estado_display()
            }
            for c in citas_pendientes
        ],
        'tiene_primera_consulta': tiene_primera_consulta,
        'tiene_finalizacion': tiene_finalizacion,
        'sesiones_seguimiento_completadas': sesiones_seguimiento,
        'puede_crear_nueva_cita': not citas_pendientes.exists()
    })

@require_GET
@login_required
def calcular_tipo_cita(request):
    """
    Calcula el tipo de cita que se asignaría a un paciente con un profesional específico.
    """
    paciente_id = request.GET.get('paciente_id')
    profesional_id = request.GET.get('profesional_id')
    
    if not paciente_id or not profesional_id:
        return JsonResponse({'error': 'Faltan parámetros'}, status=400)
    
    try:
        paciente = Patient.objects.get(pk=paciente_id)
        profesional = CustomUser.objects.get(pk=profesional_id)
        
        # Obtener citas existentes
        citas_existentes = Cita.objects.filter(
            paciente=paciente,
            profesional=profesional,
        )
        
        # Verificar citas completadas
        citas_completadas = citas_existentes.filter(estado='COMPLETADA')
        
        tiene_primera_consulta = citas_completadas.filter(
            tipo_cita='PRIMERA_CONSULTA'
        ).exists()
        
        tiene_finalizacion = citas_completadas.filter(
            tipo_cita='FINALIZACION'
        ).exists()
        
        # Determinar el tipo
        if tiene_finalizacion:
            tipo = 'REVISION'
            label = 'Revisión - Control Post-Alta'
        elif not tiene_primera_consulta:
            tipo = 'PRIMERA_CONSULTA'
            label = 'Primera Consulta - Evaluación Inicial'
        else:
            tipo = 'SEGUIMIENTO'
            label = 'Seguimiento - Sesión de Tratamiento'
        
        return JsonResponse({
            'tipo_cita': tipo,
            'label': label,
            'tiene_primera_consulta': tiene_primera_consulta,
            'tiene_finalizacion': tiene_finalizacion,
        })
    except Patient.DoesNotExist:
        return JsonResponse({'error': 'Paciente no encontrado'}, status=404)
    except CustomUser.DoesNotExist:
        return JsonResponse({'error': 'Profesional no encontrado'}, status=404)