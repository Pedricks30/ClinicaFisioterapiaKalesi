# cuestionarios/management/commands/cargar_cuestionarios_base.py
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from cuestionarios.models import Cuestionario, PreguntaCuestionario

User = get_user_model()

class Command(BaseCommand):
    help = 'Carga cuestionarios base predefinidos'
    
    def handle(self, *args, **options):
        # Buscar o crear usuario admin
        admin_user = User.objects.filter(is_superuser=True).first()
        
        if not admin_user:
            self.stdout.write(self.style.ERROR('No se encontró usuario administrador'))
            return
        
        # Cuestionario de Hombro y Pectoral
        hombro_cuestionario, created = Cuestionario.objects.get_or_create(
            nombre='Evaluación de Hombro y Pectoral',
            defaults={
                'descripcion': 'Cuestionario para evaluar dolor y funcionalidad de hombro y pectoral',
                'tipo_cuestionario': 'HOMBRO_PECTORAL',
                'activo': True,
                'created_by': admin_user
            }
        )
        
        if created:
            preguntas = [
                {
                    'texto_pregunta': '¿Sientes dolor en el hombro o pectoral en reposo?',
                    'tipo_pregunta': 'ESCALA_NUMERICA',
                    'orden': 1,
                    'obligatorio': True,
                    'escala_max': 10,
                    'etiqueta_min': 'Sin dolor',
                    'etiqueta_max': 'Máximo dolor',
                    'es_indicador_clave': True,
                    'umbral_alarma': 5
                },
                {
                    'texto_pregunta': '¿Sientes dolor al levantar el brazo o al realizar movimientos específicos?',
                    'tipo_pregunta': 'ESCALA_NUMERICA',
                    'orden': 2,
                    'obligatorio': True,
                    'escala_max': 10,
                    'etiqueta_min': 'Sin dolor',
                    'etiqueta_max': 'Dolor incapacitante',
                    'es_indicador_clave': True,
                    'umbral_alarma': 5
                },
                {
                    'texto_pregunta': '¿Puedes dormir de lado sin molestias?',
                    'tipo_pregunta': 'SI_NO',
                    'orden': 3,
                    'obligatorio': True,
                    'es_indicador_clave': True
                },
                {
                    'texto_pregunta': '¿Puedes realizar tareas de autocuidado como vestirte o peinarte sin problemas?',
                    'tipo_pregunta': 'SI_NO',
                    'orden': 4,
                    'obligatorio': True,
                    'es_indicador_clave': True
                },
                {
                    'texto_pregunta': 'Elevación anterior del brazo',
                    'tipo_pregunta': 'ESCALA_NUMERICA',
                    'orden': 5,
                    'obligatorio': True,
                    'escala_max': 10,
                    'etiqueta_min': 'Sin limitación',
                    'etiqueta_max': 'No puedo levantar',
                    'es_indicador_clave': True,
                    'umbral_alarma': 5
                },
                {
                    'texto_pregunta': 'Describe los movimientos que generan más dolor',
                    'tipo_pregunta': 'TEXTO',
                    'orden': 6,
                    'obligatorio': False
                }
            ]
            
            for pregunta_data in preguntas:
                PreguntaCuestionario.objects.create(
                    cuestionario=hombro_cuestionario,
                    **pregunta_data
                )
            
            self.stdout.write(self.style.SUCCESS(f'✓ Cuestionario "{hombro_cuestionario.nombre}" creado con {len(preguntas)} preguntas'))
        else:
            self.stdout.write(self.style.WARNING(f'✗ Cuestionario "{hombro_cuestionario.nombre}" ya existe'))