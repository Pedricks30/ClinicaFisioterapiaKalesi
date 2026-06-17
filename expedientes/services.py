# expedientes/services.py
from django.core.exceptions import ValidationError
from .models import Expediente, PrimeraConsulta, ConsultaSegumiento, ConsultaFinalizacion
# Eliminado: PlanEjerciciosDetallado - no existe en tu modelo


class ExpedienteService:
    """Servicio para manejar operaciones del expediente"""
    
    @staticmethod
    def crear_primera_consulta(expediente_id, profesional, cita=None, **datos):
        """Crea la primera consulta (solo una vez)"""
        expediente = Expediente.objects.get(id=expediente_id)
        
        if hasattr(expediente, 'primera_consulta'):
            raise ValidationError("Este expediente ya tiene una primera consulta")
        
        return PrimeraConsulta.objects.create(
            expediente=expediente,
            profesional=profesional,
            cita=cita,
            **datos
        )
    
    @staticmethod
    def crear_seguimiento(expediente_id, profesional, cita=None, **datos):
        """Crea una nueva sesión de seguimiento"""
        expediente = Expediente.objects.get(id=expediente_id)
        
        if not hasattr(expediente, 'primera_consulta'):
            raise ValidationError("Debe existir una primera consulta antes de crear seguimientos")
        
        if hasattr(expediente, 'finalizacion'):
            raise ValidationError("El tratamiento ya está finalizado, no se pueden crear más seguimientos")
        
        return ConsultaSegumiento.objects.create(
            expediente=expediente,
            profesional=profesional,
            cita=cita,
            **datos
        )
    
    @staticmethod
    def crear_finalizacion(expediente_id, profesional, cita=None, **datos):
        """Crea la consulta de finalización (solo una vez)"""
        expediente = Expediente.objects.get(id=expediente_id)
        
        if hasattr(expediente, 'finalizacion'):
            raise ValidationError("Este expediente ya tiene una consulta de finalización")
        
        if expediente.seguimientos.count() == 0:
            raise ValidationError("Debe existir al menos una sesión de seguimiento antes de finalizar")
        
        return ConsultaFinalizacion.objects.create(
            expediente=expediente,
            profesional=profesional,
            cita=cita,
            **datos
        )
    
    @staticmethod
    def obtener_historia_completa(expediente_id):
        """Obtiene toda la historia clínica del paciente"""
        expediente = Expediente.objects.get(id=expediente_id)
        
        return {
            'expediente': expediente,
            'primera_consulta': getattr(expediente, 'primera_consulta', None),
            'seguimientos': expediente.seguimientos.all().order_by('numero_sesion'),
            'finalizacion': getattr(expediente, 'finalizacion', None),
        }
    
    @staticmethod
    def obtener_evolucion_dolor(expediente_id):
        """Obtiene la evolución del dolor para gráficas"""
        expediente = Expediente.objects.get(id=expediente_id)
        
        evolucion = []
        
        # Primera consulta
        if hasattr(expediente, 'primera_consulta'):
            evolucion.append({
                'tipo': 'primera',
                'sesion': 0,
                'dolor': expediente.primera_consulta.nivel_dolor_inicial,
                'fecha': expediente.primera_consulta.fecha_consulta
            })
        
        # Seguimientos
        for sesion in expediente.seguimientos.all().order_by('numero_sesion'):
            evolucion.append({
                'tipo': 'seguimiento',
                'sesion': sesion.numero_sesion,
                'dolor': sesion.nivel_dolor_actual,
                'fecha': sesion.fecha_consulta
            })
        
        # Finalización
        if hasattr(expediente, 'finalizacion'):
            evolucion.append({
                'tipo': 'final',
                'sesion': 'final',
                'dolor': expediente.finalizacion.nivel_dolor_final,
                'fecha': expediente.finalizacion.fecha_consulta
            })
        
        return evolucion


class ManejoSesionesService:
    """Servicio específico para manejar sesiones de seguimiento dinámicamente"""
    
    @staticmethod
    def agregar_sesion(expediente_id, profesional_id, datos_sesion):
        """Agrega una nueva sesión de seguimiento"""
        expediente = Expediente.objects.get(id=expediente_id)
        # El médico puede agregar CUANTAS SESIONES NECESITE
        nueva_sesion = ConsultaSegumiento.objects.create(
            expediente=expediente,
            profesional_id=profesional_id,
            **datos_sesion
        )
        
        return nueva_sesion
    
    @staticmethod
    def recomendar_sesiones_adicionales(expediente_id, criterio_mejoria=30):
        """Recomienda si se necesitan más sesiones basado en la mejoria"""
        expediente = Expediente.objects.get(id=expediente_id)
        
        if not hasattr(expediente, 'primera_consulta'):
            return None
        
        primera = expediente.primera_consulta
        ultima_sesion = expediente.seguimientos.last()
        
        if ultima_sesion:
            mejoria = primera.nivel_dolor_inicial - ultima_sesion.nivel_dolor_actual
            porcentaje = (mejoria / primera.nivel_dolor_inicial) * 100 if primera.nivel_dolor_inicial > 0 else 100
            
            if porcentaje < criterio_mejoria:
                return {
                    'requiere_mas_sesiones': True,
                    'porcentaje_mejoria': round(porcentaje, 1),
                    'sesiones_actuales': expediente.seguimientos.count(),
                    'recomendacion': f"Mejoría del {round(porcentaje, 1)}%. Se recomiendan sesiones adicionales"
                }
        
        return {'requiere_mas_sesiones': False, 'porcentaje_mejoria': 100}
    
    @staticmethod
    def obtener_estadisticas_sesiones(expediente_id):
        """Obtiene estadísticas de las sesiones de seguimiento"""
        expediente = Expediente.objects.get(id=expediente_id)
        sesiones = expediente.seguimientos.all()
        
        if not sesiones.exists():
            return None
        
        from django.db.models import Avg
        return {
            'total_sesiones': sesiones.count(),
            'promedio_dolor': sesiones.aggregate(Avg('nivel_dolor_actual'))['nivel_dolor_actual__avg'],
            'promedio_duracion': sesiones.aggregate(Avg('duracion_sesion'))['duracion_sesion__avg'],
            'primera_sesion': sesiones.first(),
            'ultima_sesion': sesiones.last(),
        }