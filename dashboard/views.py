# views.py - Vista del dashboard con datos reales

from django.shortcuts import render
from django.utils import timezone
from django.db.models import Q
from paciente.models import Patient
from expedientes.models import Expediente
from users.models import CustomUser
from citas.models import Cita
from expedientes.models import ConsultaSegumiento
from cuestionarios.models import RespuestaCuestionario
from medical.models import Medico
from physiotherapist.models import Fisioterapeuta
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q


def dashboard(request):
    """Vista principal del dashboard con datos reales"""
    
    user = request.user
    hoy = timezone.now().date()
    ahora = timezone.now()
    
    # ============================================
    # DATOS DE PACIENTES
    # ============================================
    total_pacientes = Patient.objects.count()
    total_hombres = Patient.objects.filter(sexo='Masculino').count()
    total_mujeres = Patient.objects.filter(sexo='Femenino').count()
    
    # ============================================
    # DATOS DE PERSONAL
    # ============================================
    total_medicos = CustomUser.objects.filter(tipo_usuario='MEDIC').count()
    total_fisioterapeutas = CustomUser.objects.filter(tipo_usuario='FISIO').count()
    
    # ============================================
    # DATOS DE CITAS - FILTRADOS POR ROL
    # ============================================
    if user.tipo_usuario == 'ADMIN':
        # Admin ve TODAS las citas
        citas_query = Cita.objects.all()
        citas_pendientes_query = Cita.objects.filter(
            estado__in=['PENDIENTE', 'CONFIRMADA']
        )
        citas_hoy_query = Cita.objects.filter(fecha__date=hoy)
        
        # Notificaciones para ADMIN: todas las citas pendientes y no asistidas
        notificaciones_citas = Cita.objects.filter(
            estado__in=['PENDIENTE', 'CONFIRMADA', 'NO_ASISTIO']
        ).select_related('paciente', 'profesional').order_by('-fecha')[:10]
        
    elif user.tipo_usuario in ['MEDIC', 'FISIO']:
        # Médico o Fisioterapeuta ve SOLO sus citas
        citas_query = Cita.objects.filter(profesional=user)
        citas_pendientes_query = Cita.objects.filter(
            profesional=user,
            estado__in=['PENDIENTE', 'CONFIRMADA']
        )
        citas_hoy_query = Cita.objects.filter(
            profesional=user,
            fecha__date=hoy
        )
        
        # Notificaciones para MEDIC/FISIO: solo sus pacientes
        notificaciones_citas = Cita.objects.filter(
            profesional=user,
            estado__in=['PENDIENTE', 'CONFIRMADA', 'NO_ASISTIO']
        ).select_related('paciente', 'profesional').order_by('-fecha')[:10]
    
    else:
        # Recepcionista u otro rol ve citas del día
        citas_query = Cita.objects.all()
        citas_pendientes_query = Cita.objects.filter(
            estado__in=['PENDIENTE', 'CONFIRMADA']
        )
        citas_hoy_query = Cita.objects.filter(fecha__date=hoy)
        notificaciones_citas = Cita.objects.filter(
            estado__in=['PENDIENTE', 'CONFIRMADA', 'NO_ASISTIO']
        ).select_related('paciente', 'profesional').order_by('-fecha')[:10]
    
    # Totales de citas
    citas_hoy = citas_hoy_query.count()
    citas_pendientes = citas_pendientes_query.count()
    citas_no_asistidas = Cita.objects.filter(
        estado='NO_ASISTIO',
        fecha__date__gte=hoy - timedelta(days=7)
    ).count()
    
    # ============================================
    # CITAS POR TIPO
    # ============================================
    citas_primera = citas_query.filter(tipo_cita='PRIMERA_CONSULTA').count()
    citas_seguimiento = citas_query.filter(tipo_cita='SEGUIMIENTO').count()
    citas_finalizacion = citas_query.filter(tipo_cita='FINALIZACION').count()
    
    # ============================================
    # SESIONES Y CUESTIONARIOS
    # ============================================
    total_sesiones = ConsultaSegumiento.objects.count()
    total_cuestionarios = RespuestaCuestionario.objects.count()
    
    # ============================================
    # PRÓXIMAS CITAS (próximos 7 días)
    # ============================================
    fecha_limite = hoy + timedelta(days=7)
    
    if user.tipo_usuario in ['MEDIC', 'FISIO']:
        proximas_citas = Cita.objects.filter(
            profesional=user,
            fecha__date__gte=hoy,
            fecha__date__lte=fecha_limite,
            estado__in=['PENDIENTE', 'CONFIRMADA']
        ).select_related('paciente', 'profesional').order_by('fecha')[:10]
    else:
        proximas_citas = Cita.objects.filter(
            fecha__date__gte=hoy,
            fecha__date__lte=fecha_limite,
            estado__in=['PENDIENTE', 'CONFIRMADA']
        ).select_related('paciente', 'profesional').order_by('fecha')[:10]
    
    # ============================================
    # ACTIVIDAD RECIENTE (últimas 5 sesiones)
    # ============================================
    actividades_recientes = []
    sesiones_recientes = ConsultaSegumiento.objects.order_by('-fecha_consulta')[:5]
    
    for sesion in sesiones_recientes:
        # Solo mostrar si es admin o si el profesional es el usuario
        if user.tipo_usuario == 'ADMIN' or sesion.profesional == user:
            actividades_recientes.append({
                'paciente': sesion.expediente.paciente.get_full_name(),
                'descripcion': f'Sesión #{sesion.numero_sesion} completada',
                'fecha': sesion.fecha_consulta,
            })
    
    # ============================================
    # DATOS PARA GRÁFICOS (sesiones por mes)
    # ============================================
    meses = []
    sesiones_mes = []
    
    for i in range(11, -1, -1):
        mes = hoy.replace(day=1) - timedelta(days=i*30)
        meses.append(mes.strftime('%b'))
        inicio_mes = mes.replace(day=1)
        
        if mes.month == 12:
            fin_mes = mes.replace(year=mes.year+1, month=1, day=1)
        else:
            fin_mes = mes.replace(month=mes.month+1, day=1)
        
        count = ConsultaSegumiento.objects.filter(
            fecha_consulta__date__gte=inicio_mes,
            fecha_consulta__date__lt=fin_mes
        ).count()
        sesiones_mes.append(count)
    
    # ============================================
    # CONTEXTO PARA EL TEMPLATE
    # ============================================
    context = {
        'now': timezone.now(),
        'total_pacientes': total_pacientes,
        'total_hombres': total_hombres,
        'total_mujeres': total_mujeres,
        'total_medicos': total_medicos,
        'total_fisioterapeutas': total_fisioterapeutas,
        'citas_hoy': citas_hoy,
        'citas_pendientes': citas_pendientes,
        'citas_no_asistidas': citas_no_asistidas,
        'citas_primera': citas_primera,
        'citas_seguimiento': citas_seguimiento,
        'citas_finalizacion': citas_finalizacion,
        'total_sesiones': total_sesiones,
        'total_cuestionarios': total_cuestionarios,
        'proximas_citas': proximas_citas,
        'actividades_recientes': actividades_recientes,
        'meses_labels': meses,
        'sesiones_mes': sesiones_mes,
        'notificaciones_citas': notificaciones_citas,
        'user_tipo': user.tipo_usuario,
    }
    
    return render(request, 'inicio/index.html', context)

@login_required
def api_notificaciones_citas(request):
    """API para obtener notificaciones de citas"""
    user = request.user
    hoy = timezone.now().date()
    
    # Filtrar según rol del usuario
    if user.tipo_usuario == 'ADMIN':
        citas = Cita.objects.filter(
            estado__in=['PENDIENTE', 'CONFIRMADA']
        ).select_related('paciente', 'profesional').order_by('fecha')[:10]
    elif user.tipo_usuario in ['MEDIC', 'FISIO']:
        citas = Cita.objects.filter(
            profesional=user,
            estado__in=['PENDIENTE', 'CONFIRMADA']
        ).select_related('paciente', 'profesional').order_by('fecha')[:10]
    else:
        citas = Cita.objects.filter(
            estado__in=['PENDIENTE', 'CONFIRMADA'],
            fecha__date__gte=hoy
        ).select_related('paciente', 'profesional').order_by('fecha')[:10]
    
    data = {
        'citas': [
            {
                'id': cita.id,
                'paciente': cita.paciente.get_full_name() if cita.paciente else 'Sin paciente',
                'fecha': cita.fecha.strftime('%d/%m/%Y'),
                'hora': cita.fecha.strftime('%H:%M'),
                'estado': cita.get_estado_display(),
                'tipo': cita.tipo_cita,
                'profesional': cita.profesional.get_full_name() if cita.profesional else 'Sin profesional',
            }
            for cita in citas
        ]
    }
    return JsonResponse(data)


@login_required
def api_notificaciones_alertas(request):
    """API para obtener alertas de pacientes (no asistidos, citas canceladas, etc)"""
    user = request.user
    hoy = timezone.now().date()
    semana_pasada = hoy - timedelta(days=7)
    
    # Filtrar según rol del usuario
    if user.tipo_usuario == 'ADMIN':
        alertas = Cita.objects.filter(
            Q(estado='NO_ASISTIO') | Q(estado='CANCELADA'),
            fecha__date__gte=semana_pasada
        ).select_related('paciente', 'profesional').order_by('-fecha')[:10]
    elif user.tipo_usuario in ['MEDIC', 'FISIO']:
        alertas = Cita.objects.filter(
            Q(profesional=user, estado__in=['NO_ASISTIO', 'CANCELADA']),
            fecha__date__gte=semana_pasada
        ).select_related('paciente', 'profesional').order_by('-fecha')[:10]
    else:
        alertas = Cita.objects.filter(
            Q(estado='NO_ASISTIO') | Q(estado='CANCELADA'),
            fecha__date__gte=semana_pasada
        ).select_related('paciente', 'profesional').order_by('-fecha')[:10]
    
    data = {
        'alertas': [
            {
                'id': cita.id,
                'paciente': cita.paciente.get_full_name() if cita.paciente else 'Sin paciente',
                'fecha': cita.fecha.strftime('%d/%m/%Y'),
                'mensaje': f"No asistió a su cita" if cita.estado == 'NO_ASISTIO' else "Canceló su cita",
                'tipo': 'no_asistio' if cita.estado == 'NO_ASISTIO' else 'cancelada',
                'url': '#',
            }
            for cita in alertas
        ]
    }
    return JsonResponse(data)

# views.py - Agregar al final del archivo



@login_required
def busqueda_rapida(request):
    """API para búsqueda rápida desde el header"""
    query = request.GET.get('q', '').strip()
    
    if len(query) < 2:
        return JsonResponse({'results': []})
    
    results = []
    
    # 1. Buscar Pacientes
    pacientes = Patient.objects.filter(
        Q(nombres__icontains=query) |
        Q(apellidos__icontains=query) |
        Q(documento_identidad__icontains=query)
    )[:5]
    
    for paciente in pacientes:
        results.append({
            'id': paciente.id,
            'tipo': 'paciente',
            'titulo': paciente.get_full_name(),
            'subtitulo': f"📋 {paciente.documento_identidad}",
            'url': f"/pacientes/{paciente.id}/",
            'icono': 'fa-user',
            'color': '#2e7d64'
        })
    
    # 2. Buscar Expedientes
    expedientes = Expediente.objects.filter(
        numero_expediente__icontains=query
    )[:3]
    
    for expediente in expedientes:
        results.append({
            'id': expediente.id,
            'tipo': 'expediente',
            'titulo': f"Expediente #{expediente.numero_expediente}",
            'subtitulo': f"👤 {expediente.paciente.get_full_name()}",
            'url': f"/expedientes/{expediente.id}/",
            'icono': 'fa-folder-open',
            'color': '#4e73df'
        })
    
    # 3. Buscar Citas (si es ADMIN, MEDIC o FISIO)
    if request.user.tipo_usuario in ['ADMIN', 'MEDIC', 'FISIO']:
        citas = Cita.objects.filter(
            Q(paciente__nombres__icontains=query) |
            Q(paciente__apellidos__icontains=query) |
            Q(motivo__icontains=query)
        ).select_related('paciente', 'profesional')[:3]
        
        for cita in citas:
            results.append({
                'id': cita.id,
                'tipo': 'cita',
                'titulo': f"Cita con {cita.paciente.get_full_name()}",
                'subtitulo': f"📅 {cita.fecha.strftime('%d/%m/%Y %H:%M')} - {cita.profesional.get_full_name()}",
                'url': f"/citas/{cita.id}/",
                'icono': 'fa-calendar-alt',
                'color': '#f9a826'
            })
    
    # 4. Buscar Profesionales (solo ADMIN)
    if request.user.tipo_usuario == 'ADMIN':
        profesionales = CustomUser.objects.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(username__icontains=query)
        ).filter(tipo_usuario__in=['MEDIC', 'FISIO'])[:3]
        
        for prof in profesionales:
            results.append({
                'id': prof.id,
                'tipo': 'profesional',
                'titulo': prof.get_full_name(),
                'subtitulo': f"👨‍⚕️ {prof.get_tipo_usuario_display()}",
                'url': f"/usuarios/{prof.id}/",
                'icono': 'fa-user-md',
                'color': '#6c3483'
            })
    
    return JsonResponse({'results': results})