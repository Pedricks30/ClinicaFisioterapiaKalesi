# cuestionarios/models.py
from django.db import models
from django.conf import settings
from django.utils import timezone
import numpy as np

# =============================================================================
# MODELOS PRINCIPALES DE CUESTIONARIOS
# =============================================================================

class Cuestionario(models.Model):
    """Modelo maestro de cuestionarios"""
    
    TIPO_CUESTIONARIO = [
        ('HOMBRO_PECTORAL', 'Hombro y Pectoral'),
        ('ESPALDA', 'Espalda'),
        ('RODILLA', 'Rodilla'),
        ('CUELLO', 'Cuello'),
        ('PECHO', 'Pecho'),
        ('GENERAL', 'General'),
        ('PERSONALIZADO', 'Personalizado'),
    ]
    
    nombre = models.CharField(max_length=200, verbose_name='Nombre del cuestionario')
    descripcion = models.TextField(verbose_name='Descripción del cuestionario')
    tipo_cuestionario = models.CharField(
        max_length=50, 
        choices=TIPO_CUESTIONARIO,
        default='PERSONALIZADO',
        verbose_name='Tipo de cuestionario'
    )
    activo = models.BooleanField(default=True, verbose_name='Activo')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cuestionarios_creados'
    )
    
    class Meta:
        verbose_name = 'Cuestionario'
        verbose_name_plural = 'Cuestionarios'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.nombre} ({self.get_tipo_cuestionario_display()})"


class PreguntaCuestionario(models.Model):
    """Modelo de preguntas para los cuestionarios"""
    
    TIPO_PREGUNTA = [
        ('ESCALA', 'Escala de dolor (0-10)'),
        ('TEXTO', 'Texto libre'),
        ('SI_NO', 'Sí/No'),
        ('ESCALA_NUMERICA', 'Escala numérica (0-10)'),
        ('MULTIPLE', 'Opción múltiple'),
    ]
    
    cuestionario = models.ForeignKey(
        Cuestionario, 
        on_delete=models.CASCADE, 
        related_name='preguntas',
        verbose_name='Cuestionario'
    )
    texto_pregunta = models.TextField(verbose_name='Texto de la pregunta')
    tipo_pregunta = models.CharField(max_length=20, choices=TIPO_PREGUNTA, verbose_name='Tipo de pregunta')
    orden = models.PositiveIntegerField(default=0, verbose_name='Orden de la pregunta')
    obligatorio = models.BooleanField(default=True, verbose_name='Obligatorio')
    
    # Para preguntas de opción múltiple (almacenar opciones como JSON)
    opciones = models.JSONField(null=True, blank=True, verbose_name='Opciones (para múltiple)')
    
    # Configuración adicional para escalas
    escala_min = models.IntegerField(default=0, verbose_name='Valor mínimo de escala')
    escala_max = models.IntegerField(default=10, verbose_name='Valor máximo de escala')
    etiqueta_min = models.CharField(max_length=100, blank=True, verbose_name='Etiqueta valor mínimo')
    etiqueta_max = models.CharField(max_length=100, blank=True, verbose_name='Etiqueta valor máximo')
    
    # Para análisis predictivo
    es_indicador_clave = models.BooleanField(default=False, verbose_name='Es indicador clave de evolución')
    umbral_alarma = models.IntegerField(null=True, blank=True, verbose_name='Umbral de alarma (0-10)')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Pregunta del Cuestionario'
        verbose_name_plural = 'Preguntas del Cuestionario'
        ordering = ['cuestionario', 'orden']
    
    def __str__(self):
        return f"{self.cuestionario.nombre} - {self.texto_pregunta[:50]}"


class RespuestaCuestionario(models.Model):
    """Modelo de respuestas de cuestionarios (genérico)"""
    
    # Relación con la consulta de seguimiento (ForeignKey a tu app principal)
    consulta_seguimiento = models.ForeignKey(
        'expedientes.ConsultaSegumiento',  # Ajusta el nombre de tu app
        on_delete=models.CASCADE,
        related_name='respuestas_cuestionario',
        verbose_name='Consulta de seguimiento'
    )
    
    # Relación con la pregunta
    pregunta = models.ForeignKey(
        PreguntaCuestionario,
        on_delete=models.CASCADE,
        related_name='respuestas',
        verbose_name='Pregunta'
    )
    
    # Almacenamiento de respuestas según tipo
    respuesta_texto = models.TextField(blank=True, null=True, verbose_name='Respuesta texto')
    respuesta_escala = models.IntegerField(null=True, blank=True, verbose_name='Respuesta escala')
    respuesta_booleana = models.BooleanField(null=True, blank=True, verbose_name='Respuesta Sí/No')
    respuesta_multiple = models.CharField(max_length=500, blank=True, null=True, verbose_name='Respuesta múltiple')
    
    # Metadata
    fecha_respuesta = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de respuesta')
    ip_usuario = models.GenericIPAddressField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Respuesta del Cuestionario'
        verbose_name_plural = 'Respuestas de Cuestionarios'
        unique_together = [['consulta_seguimiento', 'pregunta']]
    
    def __str__(self):
        return f"Respuesta de {self.consulta_seguimiento} - {self.pregunta.texto_pregunta[:30]}"
    
    @property
    def valor_respuesta(self):
        """Devuelve la respuesta según su tipo"""
        if self.pregunta.tipo_pregunta in ['ESCALA', 'ESCALA_NUMERICA']:
            return self.respuesta_escala
        elif self.pregunta.tipo_pregunta == 'TEXTO':
            return self.respuesta_texto
        elif self.pregunta.tipo_pregunta == 'SI_NO':
            return self.respuesta_booleana
        elif self.pregunta.tipo_pregunta == 'MULTIPLE':
            return self.respuesta_multiple
        return None


# =============================================================================
# MODELOS PARA ANÁLISIS PREDICTIVO
# =============================================================================

class AnalisisPredictivoEscala(models.Model):
    """
    Tabla especializada para almacenar respuestas de escala (0-10)
    y facilitar análisis evolutivos y predictivos
    """
    
    # Relaciones
    consulta_seguimiento = models.ForeignKey(
        'expedientes.ConsultaSegumiento',
        on_delete=models.CASCADE,
        related_name='analisis_predictivos',
        verbose_name='Consulta de seguimiento'
    )
    pregunta = models.ForeignKey(
        PreguntaCuestionario,
        on_delete=models.CASCADE,
        related_name='analisis_predictivos',
        verbose_name='Pregunta de escala'
    )
    
    # Datos de la escala
    valor_escala = models.IntegerField(
        null=True, blank=True,
        verbose_name='Valor numérico (0-10)'
    )
    valor_normalizado = models.FloatField(
        null=True, blank=True,
        verbose_name='Valor normalizado (0-1)'
    )
    
    # Metadatos para análisis
    sesion_numero = models.PositiveIntegerField(verbose_name='Número de sesión')
    fecha_consulta = models.DateTimeField(verbose_name='Fecha de consulta')
    profesional = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='analisis_realizados'
    )
    
    # Campos para tendencias y predicciones
    tendencia = models.CharField(
        max_length=20,
        choices=[
            ('MEJORANDO', 'Mejorando'),
            ('ESTABLE', 'Estable'),
            ('EMPEORANDO', 'Empeorando'),
            ('SIN_DATOS', 'Sin datos suficientes'),
        ],
        default='SIN_DATOS',
        verbose_name='Tendencia'
    )
    variacion_porcentual = models.FloatField(
        null=True, blank=True,
        verbose_name='Variación respecto a sesión anterior (%)'
    )
    
    # Análisis predictivo
    prediccion_siguiente = models.IntegerField(
        null=True, blank=True,
        verbose_name='Predicción para siguiente sesión'
    )
    intervalo_confianza_min = models.IntegerField(
        null=True, blank=True,
        verbose_name='Intervalo de confianza mínimo'
    )
    intervalo_confianza_max = models.IntegerField(
        null=True, blank=True,
        verbose_name='Intervalo de confianza máximo'
    )
    
    # Flags para análisis
    es_linea_base = models.BooleanField(
        default=False,
        verbose_name='Es valor base (primera medición)'
    )
    supera_umbral_alarma = models.BooleanField(
        default=False,
        verbose_name='Supera umbral de alarma'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Análisis Predictivo de Escala'
        verbose_name_plural = 'Análisis Predictivos de Escalas'
        ordering = ['pregunta', 'sesion_numero']
        unique_together = [['consulta_seguimiento', 'pregunta']]
    
    def __str__(self):
        return f"Sesión {self.sesion_numero} - {self.pregunta.texto_pregunta[:30]} - Valor: {self.valor_escala}"
    
    def save(self, *args, **kwargs):
        if self.valor_escala is not None:
            self.valor_normalizado = round(self.valor_escala / 10.0, 2)
            # Verificar umbral de alarma de la pregunta
            if self.pregunta.umbral_alarma and self.valor_escala >= self.pregunta.umbral_alarma:
                self.supera_umbral_alarma = True
            else:
                self.supera_umbral_alarma = False
        super().save(*args, **kwargs)


class EvolucionPaciente(models.Model):
    """
    Tabla resumen para visualización rápida de evolución
    """
    
    expediente = models.ForeignKey(
        'expedientes.Expediente',
        on_delete=models.CASCADE,
        related_name='evoluciones_cuestionarios'
    )
    
    # Resumen por tipo de evaluación
    tipo_evaluacion = models.CharField(
        max_length=100,
        verbose_name='Tipo de evaluación'
    )
    pregunta_relacionada = models.ForeignKey(
        PreguntaCuestionario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='evoluciones'
    )
    
    # Datos agregados
    primera_medicion = models.FloatField(verbose_name='Primera medición')
    ultima_medicion = models.FloatField(verbose_name='Última medición')
    mejor_valor = models.FloatField(verbose_name='Mejor valor alcanzado')
    peor_valor = models.FloatField(verbose_name='Peor valor registrado')
    promedio = models.FloatField(verbose_name='Promedio histórico')
    
    # Indicadores de progreso
    mejoria_total = models.FloatField(verbose_name='Mejoría total')
    porcentaje_mejoria = models.FloatField(verbose_name='Porcentaje de mejoría')
    tendencia_general = models.CharField(
        max_length=20,
        choices=[
            ('MEJORANDO', 'Mejorando'),
            ('ESTABLE', 'Estable'),
            ('EMPEORANDO', 'Empeorando'),
        ],
        verbose_name='Tendencia general'
    )
    
    # Datos para gráficos (guardados como JSON)
    evolucion_historica = models.JSONField(
        default=list,
        verbose_name='Datos históricos para gráficos'
    )
    
    # Metadatos
    ultima_actualizacion = models.DateTimeField(auto_now=True)
    numero_sesiones = models.PositiveIntegerField(default=0)
    
    class Meta:
        verbose_name = 'Evolución del Paciente'
        verbose_name_plural = 'Evoluciones de Pacientes'
        unique_together = [['expediente', 'pregunta_relacionada']]
    
    def __str__(self):
        return f"{self.expediente} - {self.tipo_evaluacion} - Mejoría: {self.porcentaje_mejoria}%"