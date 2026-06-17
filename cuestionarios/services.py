# cuestionarios/services.py logica de negocios
from django.db.models import Avg
import numpy as np
from .models import AnalisisPredictivoEscala, EvolucionPaciente

class AnalisisPredictivoService:
    """Servicio para manejar análisis predictivos"""
    
    def sincronizar_respuesta_escala(self, respuesta_cuestionario):
        """Sincroniza respuesta de escala con análisis predictivo"""
        pregunta = respuesta_cuestionario.pregunta
        
        # Solo procesar preguntas de tipo escala
        if pregunta.tipo_pregunta in ['ESCALA', 'ESCALA_NUMERICA'] and respuesta_cuestionario.respuesta_escala is not None:
            
            consulta = respuesta_cuestionario.consulta_seguimiento
            
            # Crear o actualizar análisis predictivo
            analisis, created = AnalisisPredictivoEscala.objects.update_or_create(
                consulta_seguimiento=consulta,
                pregunta=pregunta,
                defaults={
                    'valor_escala': respuesta_cuestionario.respuesta_escala,
                    'sesion_numero': consulta.numero_sesion,
                    'fecha_consulta': consulta.fecha_consulta,
                    'profesional': consulta.profesional,
                    'es_linea_base': consulta.numero_sesion == 1,
                }
            )
            
            # Recalcular tendencias
            self.calcular_tendencias_y_predicciones(pregunta.id, consulta.expediente.id)
            
            # Actualizar evolución del paciente
            self.actualizar_evolucion_paciente(consulta.expediente, pregunta)
            
            return analisis
        return None
    
    def calcular_tendencias_y_predicciones(self, pregunta_id, expediente_id):
        """
        Calcula tendencias y predicciones para una pregunta específica
        de un expediente usando regresión lineal simple
        """
        # Obtener todas las mediciones
        mediciones = AnalisisPredictivoEscala.objects.filter(
            pregunta_id=pregunta_id,
            consulta_seguimiento__expediente_id=expediente_id
        ).order_by('sesion_numero')
        
        if mediciones.count() < 2:
            return
        
        # Calcular tendencia
        valores = list(mediciones.values_list('valor_escala', flat=True))
        ultimo = valores[-1]
        primero = valores[0]
        
        if ultimo < primero:
            tendencia = 'MEJORANDO'
        elif ultimo > primero:
            tendencia = 'EMPEORANDO'
        else:
            tendencia = 'ESTABLE'
        
        # Calcular variación porcentual
        if len(valores) >= 2:
            variacion = ((valores[-1] - valores[-2]) / valores[-2]) * 100 if valores[-2] != 0 else 0
        else:
            variacion = 0
        
        # Regresión lineal simple para predicción
        if len(valores) >= 3:
            x = np.arange(len(valores))
            y = np.array(valores)
            
            z = np.polyfit(x, y, 1)
            pendiente = z[0]
            intercepto = z[1]
            
            siguiente_x = len(valores)
            prediccion = pendiente * siguiente_x + intercepto
            prediccion = max(0, min(10, prediccion))
            
            residuos = y - (pendiente * x + intercepto)
            std_residuos = np.std(residuos)
            
            intervalo_min = max(0, int(prediccion - std_residuos))
            intervalo_max = min(10, int(prediccion + std_residuos))
            
            ultima_medicion = mediciones.last()
            ultima_medicion.prediccion_siguiente = int(round(prediccion))
            ultima_medicion.intervalo_confianza_min = intervalo_min
            ultima_medicion.intervalo_confianza_max = intervalo_max
            ultima_medicion.tendencia = tendencia
            ultima_medicion.variacion_porcentual = round(variacion, 2)
            ultima_medicion.save()
        else:
            ultima_medicion = mediciones.last()
            ultima_medicion.tendencia = tendencia
            ultima_medicion.variacion_porcentual = round(variacion, 2) if len(valores) >= 2 else None
            ultima_medicion.save()
    
    def actualizar_evolucion_paciente(self, expediente, pregunta):
        """Actualiza los datos de evolución del paciente"""
        
        analisis = AnalisisPredictivoEscala.objects.filter(
            consulta_seguimiento__expediente=expediente,
            pregunta=pregunta
        ).order_by('sesion_numero')
        
        if not analisis.exists():
            return
        
        valores = list(analisis.values_list('valor_escala', flat=True))
        fechas = list(analisis.values_list('fecha_consulta', flat=True))
        sesiones = list(analisis.values_list('sesion_numero', flat=True))
        
        evolucion, _ = EvolucionPaciente.objects.update_or_create(
            expediente=expediente,
            pregunta_relacionada=pregunta,
            defaults={
                'tipo_evaluacion': pregunta.texto_pregunta[:100],
                'primera_medicion': valores[0],
                'ultima_medicion': valores[-1],
                'mejor_valor': min(valores),
                'peor_valor': max(valores),
                'promedio': sum(valores) / len(valores),
                'mejoria_total': valores[0] - valores[-1],
                'porcentaje_mejoria': ((valores[0] - valores[-1]) / valores[0]) * 100 if valores[0] != 0 else 0,
                'evolucion_historica': [
                    {
                        'sesion': sesiones[i],
                        'fecha': fechas[i].strftime('%Y-%m-%d'),
                        'valor': valores[i],
                        'normalizado': valores[i] / 10
                    }
                    for i in range(len(valores))
                ],
                'numero_sesiones': len(valores),
                'tendencia_general': self.calcular_tendencia_general(valores)
            }
        )
        
        return evolucion
    
    def calcular_tendencia_general(self, valores):
        """Calcula tendencia general basada en los valores"""
        if len(valores) < 2:
            return 'ESTABLE'
        
        # Usar regresión lineal para determinar tendencia
        x = np.arange(len(valores))
        y = np.array(valores)
        z = np.polyfit(x, y, 1)
        pendiente = z[0]
        
        if pendiente < -0.1:  # Mejorando (pendiente negativa)
            return 'MEJORANDO'
        elif pendiente > 0.1:  # Empeorando (pendiente positiva)
            return 'EMPEORANDO'
        else:
            return 'ESTABLE'