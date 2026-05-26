from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from datetime import datetime, timedelta
from django.db import models
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
    
    # Médicos con esta especialidad
    medicos_ids = Medico.objects.filter(specialties_id=especialidad_id).values_list('user_id', flat=True)
    # Fisioterapeutas con esta especialidad
    fisios_ids = Fisioterapeuta.objects.filter(specialties_id=especialidad_id).values_list('user_id', flat=True)
    
    todos_ids = list(medicos_ids) + list(fisios_ids)
    
    profesionales = CustomUser.objects.filter(
        id__in=todos_ids,
        tipo_usuario__in=['MEDIC', 'FISIO'],
        is_active=True
    ).order_by('first_name', 'last_name')
    
    data = [{
        'id': p.id,
        'nombre': p.get_full_name(),
        'tipo': p.get_tipo_usuario_display(),
        'especialidad': p.perfil_profesional.specialties.specialties if p.perfil_profesional and p.perfil_profesional.specialties else '',
        'horarios': _get_horarios_resumen(p)
    } for p in profesionales]
    
    return JsonResponse({'profesionales': data})


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
        data.append({
            'id': h.id,
            'dias': h.get_dias_display(),
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
        estado__in=['PENDIENTE', 'CONFIRMADA', 'EN_PROCESO']
    )
    
    slots_disponibles = []
    for horario in horarios:
        inicio = datetime.combine(fecha, horario.hora_inicio)
        fin = datetime.combine(fecha, horario.hora_fin)
        current = inicio
        
        while current + timedelta(minutes=30) <= fin:
            slot_fin = current + timedelta(minutes=30)
            
            disponible = True
            for cita in citas_existentes:
                cita_fin = cita.fecha + timedelta(minutes=cita.duracion)
                if (current < cita_fin) and (slot_fin > cita.fecha):
                    disponible = False
                    break
            
            if disponible:
                slots_disponibles.append({
                    'hora': current.strftime('%H:%M'),
                    'hora_fin': slot_fin.strftime('%H:%M'),
                    'datetime': current.strftime('%Y-%m-%dT%H:%M'),
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
    
    # Filtros según tipo de usuario
    user = request.user
    if user.is_medico or user.is_fisio:
        citas = citas.filter(profesional=user)
    elif user.is_recepcionista or user.is_admin:
        pass  # Ve todas
    else:
        citas = citas.none()
    
    events = []
    for cita in citas:
        events.append({
            'id': cita.id,
            'title': f"{cita.paciente.apellidos}, {cita.paciente.nombres[:1]}. - {cita.motivo[:30]}",
            'start': cita.fecha.isoformat(),
            'end': (cita.fecha + timedelta(minutes=cita.duracion)).isoformat(),
            'backgroundColor': cita.notas_internas if cita.notas_internas and cita.notas_internas.startswith('#') else '#007BFF',
            'borderColor': '#000',
            'extendedProps': {
                'paciente_id': cita.paciente.id,
                'paciente_nombre': cita.paciente.get_full_name(),
                'profesional_id': cita.profesional.id,
                'profesional_nombre': cita.profesional.get_full_name(),
                'motivo': cita.motivo,
                'estado': cita.estado,
                'duracion': cita.duracion,
                'tipo_cita': cita.get_tipo_cita_display(),
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
    if user.is_medico or user.is_fisio:
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
    horarios = Horario.objects.filter(profesional=profesional, disponible=True)
    if horarios.exists():
        h = horarios.first()
        return f"{', '.join(h.get_dias_display())} | {h.hora_inicio.strftime('%H:%M')}-{h.hora_fin.strftime('%H:%M')}"
    return "Sin horario asignado"


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


# Necesario para la búsqueda
