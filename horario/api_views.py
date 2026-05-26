# horarios/api_views.py
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.contrib.auth.decorators import login_required
from users.models import CustomUser, Specialties
from medical.models import Medico
from physiotherapist.models import Fisioterapeuta


# -------------------------------------------------------------------------
# API PARA FILTRAR PROFESIONALES POR ESPECIALIDAD
# -------------------------------------------------------------------------
@require_GET
@login_required
def filtrar_profesionales(request):
    """
    API: Retorna JSON con los profesionales que tienen la especialidad seleccionada.
    Busca en Medico.specialties y Fisioterapeuta.specialties.
    
    Parámetros GET:
        especialidad: ID de la especialidad
    
    Retorna:
        JSON con lista de profesionales y conteo
    """
    especialidad_id = request.GET.get('especialidad')
    
    if not especialidad_id:
        return JsonResponse({
            'profesionales': [], 
            'count': 0,
            'mensaje': 'No se proporcionó especialidad'
        })
    
    try:
        especialidad_id = int(especialidad_id)
        
        # Verificar que la especialidad existe
        if not Specialties.objects.filter(id_specialty=especialidad_id).exists():
            return JsonResponse({
                'profesionales': [], 
                'count': 0,
                'mensaje': 'Especialidad no encontrada'
            }, status=404)
        
        # Obtener IDs de médicos con esta especialidad
        medicos_ids = Medico.objects.filter(
            specialties_id=especialidad_id
        ).values_list('user_id', flat=True)
        
        # Obtener IDs de fisioterapeutas con esta especialidad
        fisios_ids = Fisioterapeuta.objects.filter(
            specialties_id=especialidad_id
        ).values_list('user_id', flat=True)
        
        # Combinar todos los IDs
        todos_ids = list(medicos_ids) + list(fisios_ids)
        
        # Obtener los usuarios profesionales
        profesionales = CustomUser.objects.filter(
            id__in=todos_ids,
            tipo_usuario__in=['MEDIC', 'FISIO'],
            is_active=True
        ).order_by('first_name', 'last_name')
        
        profesionales_data = []
        # En api_views.py, corrige la parte donde obtienes el perfil:
        for p in profesionales:
            # Obtener especialidad según el tipo de usuario
            especialidad_nombre = 'Sin especialidad'
            if p.tipo_usuario == 'MEDIC' and hasattr(p, 'perfil_medico'):
                especialidad_nombre = p.perfil_medico.specialties.specialties if p.perfil_medico.specialties else 'Sin especialidad'
            elif p.tipo_usuario == 'FISIO' and hasattr(p, 'perfil_fisioterapeuta'):
                especialidad_nombre = p.perfil_fisioterapeuta.specialties.specialties if p.perfil_fisioterapeuta.specialties else 'Sin especialidad'
            
            profesionales_data.append({
                'id': p.id,
                'nombre_completo': p.get_full_name(),
                'tipo': p.get_tipo_usuario_display(),
                'documento': p.document_number,
                'especialidad': especialidad_nombre,
            })
        
        return JsonResponse({
            'profesionales': profesionales_data,
            'count': len(profesionales_data)
        })
    
    except ValueError:
        return JsonResponse({
            'error': 'ID de especialidad inválido',
            'profesionales': [],
            'count': 0
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'error': f'Error al filtrar profesionales: {str(e)}',
            'profesionales': [],
            'count': 0
        }, status=500)