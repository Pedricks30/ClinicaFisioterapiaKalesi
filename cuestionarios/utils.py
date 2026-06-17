# cuestionarios/utils.py
import json
from django.core.serializers.json import DjangoJSONEncoder
from .models import Cuestionario, PreguntaCuestionario

def exportar_cuestionario_json(cuestionario_id):
    """Exporta un cuestionario completo a JSON"""
    cuestionario = Cuestionario.objects.prefetch_related('preguntas').get(pk=cuestionario_id)
    
    data = {
        'nombre': cuestionario.nombre,
        'descripcion': cuestionario.descripcion,
        'tipo_cuestionario': cuestionario.tipo_cuestionario,
        'preguntas': []
    }
    
    for pregunta in cuestionario.preguntas.all().order_by('orden'):
        data['preguntas'].append({
            'texto_pregunta': pregunta.texto_pregunta,
            'tipo_pregunta': pregunta.tipo_pregunta,
            'orden': pregunta.orden,
            'obligatorio': pregunta.obligatorio,
            'opciones': pregunta.opciones,
            'escala_min': pregunta.escala_min,
            'escala_max': pregunta.escala_max,
            'etiqueta_min': pregunta.etiqueta_min,
            'etiqueta_max': pregunta.etiqueta_max,
            'es_indicador_clave': pregunta.es_indicador_clave,
            'umbral_alarma': pregunta.umbral_alarma
        })
    
    return json.dumps(data, cls=DjangoJSONEncoder, indent=2)

def importar_cuestionario_json(json_data, usuario=None):
    """Importa un cuestionario desde JSON"""
    data = json.loads(json_data)
    
    cuestionario = Cuestionario.objects.create(
        nombre=data['nombre'],
        descripcion=data['descripcion'],
        tipo_cuestionario=data['tipo_cuestionario'],
        created_by=usuario
    )
    
    for pregunta_data in data['preguntas']:
        PreguntaCuestionario.objects.create(
            cuestionario=cuestionario,
            **pregunta_data
        )
    
    return cuestionario