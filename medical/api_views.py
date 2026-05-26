from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db import models
from users.models import CustomUser
from .models import Medico


@login_required
def buscar_medicos(request):
    """
    API para buscar usuarios de tipo MEDIC que NO tengan perfil médico asignado.
    Retorna resultados en formato compatible con Select2.
    """
    query = request.GET.get('q', '').strip()
    
    if len(query) < 2:
        return JsonResponse({'results': [], 'more': False})
    
    # Obtener IDs de médicos que ya tienen perfil
    medicos_con_perfil = Medico.objects.values_list('user_id', flat=True)
    
    # Buscar usuarios MEDIC que NO tengan perfil asignado
    usuarios = CustomUser.objects.filter(
        tipo_usuario='MEDIC'
    ).exclude(
        id__in=medicos_con_perfil
    ).filter(
        models.Q(first_name__icontains=query) |
        models.Q(last_name__icontains=query) |
        models.Q(email__icontains=query) |
        models.Q(document_number__icontains=query)
    ).distinct()[:20]
    
    results = []
    for user in usuarios:
        results.append({
            'id': user.id,
            'text': user.get_full_name() or user.username,
            'email': user.email,
            'document_number': user.document_number,
            'profile_image_url': user.profile_image.url if user.profile_image else None,
        })
    
    return JsonResponse({
        'results': results,
        'more': len(results) == 20
    })