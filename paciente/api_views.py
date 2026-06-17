# paciente/api_views.py
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.contrib.auth.decorators import login_required
from django.db import models
from .models import Patient


@require_GET
@login_required
def buscar_pacientes(request):
    """
    Endpoint para buscar pacientes por nombre, apellido o documento.
    Retorna JSON para Select2.
    """
    q = request.GET.get('q', '').strip()
    
    if not q or len(q) < 2:
        return JsonResponse({'results': []})
    
    pacientes = Patient.objects.filter(
        estado=True
    ).filter(
        models.Q(nombres__icontains=q) |
        models.Q(apellidos__icontains=q) |
        models.Q(documento_identidad__icontains=q)
    ).order_by('apellidos', 'nombres')[:20]
    
    results = []
    for paciente in pacientes:
        results.append({
            'id': paciente.id,
            'text': f"{paciente.get_full_name()} - {paciente.tipo_documento} ({paciente.documento_identidad})",
            'documento': paciente.documento_identidad,
            'nombre_completo': f"{paciente.nombres} {paciente.apellidos}"
        })
    
    return JsonResponse({'results': results})