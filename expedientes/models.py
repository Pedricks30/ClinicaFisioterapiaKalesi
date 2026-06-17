from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from paciente.models import Patient
from users.models import CustomUser
# =============================================================================
# MODELOS ABSTRACTOS BASE PARA REUTILIZACIÓN
# =============================================================================
class BaseEvaluacionDolor(models.Model):
    """Modelo abstracto para evaluación de dolor"""
    
    NIVEL_DOLOR = [
        (0, '0 - Sin dolor'), (1, '1 - Dolor muy leve'), (2, '2 - Dolor leve'),
        (3, '3 - Dolor moderado'), (4, '4 - Dolor moderado-alto'),
        (5, '5 - Dolor alto'), (6, '6 - Dolor muy alto'), (7, '7 - Dolor severo'),
        (8, '8 - Dolor muy severo'), (9, '9 - Dolor extremadamente severo'),
        (10, '10 - Máximo dolor imaginable'),
    ]
    
    nivel_dolor = models.IntegerField(choices=NIVEL_DOLOR, null=True, blank=True, verbose_name='Nivel de dolor')
    localizacion_dolor = models.TextField(blank=True, verbose_name='Localización del dolor')
    
    class Meta:
        abstract = True

class BaseEvaluacionMuscular(models.Model):
    """Modelo abstracto para evaluación muscular (grados 0-5)"""
    
    GRADO_FUERZA_MUSCULAR = [
        (0, '0 - Ausencia de contracción muscular'),
        (1, '1 - Esbozo de contracción muscular'),
        (2, '2 - Movimiento activo que no puede vencer la gravedad'),
        (3, '3 - Movimiento contra gravedad sin resistencia'),
        (4, '4 - Movimiento contra resistencia reducida'),
        (5, '5 - Fuerza muscular normal contra resistencia completa'),
    ]
    
    # Miembros Superiores - Evaluación 1 y 2
    ms_eval1_izquierda = models.IntegerField(choices=GRADO_FUERZA_MUSCULAR, null=True, blank=True, verbose_name='M. SUP. Evaluación 1 - Izquierda')
    ms_eval1_derecha = models.IntegerField(choices=GRADO_FUERZA_MUSCULAR, null=True, blank=True, verbose_name='M. SUP. Evaluación 1 - Derecha')
    ms_eval2_izquierda = models.IntegerField(choices=GRADO_FUERZA_MUSCULAR, null=True, blank=True, verbose_name='M. SUP. Evaluación 2 - Izquierda')
    ms_eval2_derecha = models.IntegerField(choices=GRADO_FUERZA_MUSCULAR, null=True, blank=True, verbose_name='M. SUP. Evaluación 2 - Derecha')
    
    # Miembros Inferiores - Evaluación 1 y 2
    mi_eval1_izquierda = models.IntegerField(choices=GRADO_FUERZA_MUSCULAR, null=True, blank=True, verbose_name='M. INF. Evaluación 1 - Izquierda')
    mi_eval1_derecha = models.IntegerField(choices=GRADO_FUERZA_MUSCULAR, null=True, blank=True, verbose_name='M. INF. Evaluación 1 - Derecha')
    mi_eval2_izquierda = models.IntegerField(choices=GRADO_FUERZA_MUSCULAR, null=True, blank=True, verbose_name='M. INF. Evaluación 2 - Izquierda')
    mi_eval2_derecha = models.IntegerField(choices=GRADO_FUERZA_MUSCULAR, null=True, blank=True, verbose_name='M. INF. Evaluación 2 - Derecha')
    
    # Tronco - Evaluación 1 y 2
    tronco_eval1_izquierda = models.IntegerField(choices=GRADO_FUERZA_MUSCULAR, null=True, blank=True, verbose_name='Tronco Evaluación 1 - Izquierda')
    tronco_eval1_derecha = models.IntegerField(choices=GRADO_FUERZA_MUSCULAR, null=True, blank=True, verbose_name='Tronco Evaluación 1 - Derecha')
    tronco_eval2_izquierda = models.IntegerField(choices=GRADO_FUERZA_MUSCULAR, null=True, blank=True, verbose_name='Tronco Evaluación 2 - Izquierda')
    tronco_eval2_derecha = models.IntegerField(choices=GRADO_FUERZA_MUSCULAR, null=True, blank=True, verbose_name='Tronco Evaluación 2 - Derecha')
    
    # Cuello - Evaluación 1 y 2
    cuello_eval1_izquierda = models.IntegerField(choices=GRADO_FUERZA_MUSCULAR, null=True, blank=True, verbose_name='Cuello Evaluación 1 - Izquierda')
    cuello_eval1_derecha = models.IntegerField(choices=GRADO_FUERZA_MUSCULAR, null=True, blank=True, verbose_name='Cuello Evaluación 1 - Derecha')
    cuello_eval2_izquierda = models.IntegerField(choices=GRADO_FUERZA_MUSCULAR, null=True, blank=True, verbose_name='Cuello Evaluación 2 - Izquierda')
    cuello_eval2_derecha = models.IntegerField(choices=GRADO_FUERZA_MUSCULAR, null=True, blank=True, verbose_name='Cuello Evaluación 2 - Derecha')
    
    class Meta:
        abstract = True

class BaseEvaluacionGoniometrica(models.Model):
    """Modelo abstracto para evaluación goniométrica (rangos de movimiento)"""
    
    # ==================== MIEMBROS SUPERIORES ====================
    # Evaluación 1
    ms_flexion_eval1_izq = models.IntegerField(null=True, blank=True, verbose_name='M. SUP. Eval1 - Flexión Izq (°)')
    ms_flexion_eval1_der = models.IntegerField(null=True, blank=True, verbose_name='M. SUP. Eval1 - Flexión Der (°)')
    ms_extension_eval1_izq = models.IntegerField(null=True, blank=True, verbose_name='M. SUP. Eval1 - Extensión Izq (°)')
    ms_extension_eval1_der = models.IntegerField(null=True, blank=True, verbose_name='M. SUP. Eval1 - Extensión Der (°)')
    ms_abduccion_eval1_izq = models.IntegerField(null=True, blank=True, verbose_name='M. SUP. Eval1 - Abducción Izq (°)')
    ms_abduccion_eval1_der = models.IntegerField(null=True, blank=True, verbose_name='M. SUP. Eval1 - Abducción Der (°)')
    
    # Evaluación 2
    ms_flexion_eval2_izq = models.IntegerField(null=True, blank=True, verbose_name='M. SUP. Eval2 - Flexión Izq (°)')
    ms_flexion_eval2_der = models.IntegerField(null=True, blank=True, verbose_name='M. SUP. Eval2 - Flexión Der (°)')
    ms_extension_eval2_izq = models.IntegerField(null=True, blank=True, verbose_name='M. SUP. Eval2 - Extensión Izq (°)')
    ms_extension_eval2_der = models.IntegerField(null=True, blank=True, verbose_name='M. SUP. Eval2 - Extensión Der (°)')
    ms_abduccion_eval2_izq = models.IntegerField(null=True, blank=True, verbose_name='M. SUP. Eval2 - Abducción Izq (°)')
    ms_abduccion_eval2_der = models.IntegerField(null=True, blank=True, verbose_name='M. SUP. Eval2 - Abducción Der (°)')
    
    # ==================== MIEMBROS INFERIORES ====================
    # Evaluación 1
    mi_flexion_eval1_izq = models.IntegerField(null=True, blank=True, verbose_name='M. INF. Eval1 - Flexión Izq (°)')
    mi_flexion_eval1_der = models.IntegerField(null=True, blank=True, verbose_name='M. INF. Eval1 - Flexión Der (°)')
    mi_extension_eval1_izq = models.IntegerField(null=True, blank=True, verbose_name='M. INF. Eval1 - Extensión Izq (°)')
    mi_extension_eval1_der = models.IntegerField(null=True, blank=True, verbose_name='M. INF. Eval1 - Extensión Der (°)')
    
    # Evaluación 2
    mi_flexion_eval2_izq = models.IntegerField(null=True, blank=True, verbose_name='M. INF. Eval2 - Flexión Izq (°)')
    mi_flexion_eval2_der = models.IntegerField(null=True, blank=True, verbose_name='M. INF. Eval2 - Flexión Der (°)')
    mi_extension_eval2_izq = models.IntegerField(null=True, blank=True, verbose_name='M. INF. Eval2 - Extensión Izq (°)')
    mi_extension_eval2_der = models.IntegerField(null=True, blank=True, verbose_name='M. INF. Eval2 - Extensión Der (°)')
    
    # ==================== TRONCO ====================
    # Evaluación 1
    tronco_flexion_eval1 = models.IntegerField(null=True, blank=True, verbose_name='Tronco Eval1 - Flexión (°)')
    tronco_extension_eval1 = models.IntegerField(null=True, blank=True, verbose_name='Tronco Eval1 - Extensión (°)')
    tronco_lateral_izq_eval1 = models.IntegerField(null=True, blank=True, verbose_name='Tronco Eval1 - Lateral Izq (°)')
    tronco_lateral_der_eval1 = models.IntegerField(null=True, blank=True, verbose_name='Tronco Eval1 - Lateral Der (°)')
    
    # Evaluación 2
    tronco_flexion_eval2 = models.IntegerField(null=True, blank=True, verbose_name='Tronco Eval2 - Flexión (°)')
    tronco_extension_eval2 = models.IntegerField(null=True, blank=True, verbose_name='Tronco Eval2 - Extensión (°)')
    tronco_lateral_izq_eval2 = models.IntegerField(null=True, blank=True, verbose_name='Tronco Eval2 - Lateral Izq (°)')
    tronco_lateral_der_eval2 = models.IntegerField(null=True, blank=True, verbose_name='Tronco Eval2 - Lateral Der (°)')
    
    # ==================== CUELLO ====================
    # Evaluación 1
    cuello_flexion_eval1 = models.IntegerField(null=True, blank=True, verbose_name='Cuello Eval1 - Flexión (°)')
    cuello_extension_eval1 = models.IntegerField(null=True, blank=True, verbose_name='Cuello Eval1 - Extensión (°)')
    cuello_lateral_izq_eval1 = models.IntegerField(null=True, blank=True, verbose_name='Cuello Eval1 - Lateral Izq (°)')
    cuello_lateral_der_eval1 = models.IntegerField(null=True, blank=True, verbose_name='Cuello Eval1 - Lateral Der (°)')
    cuello_rotacion_izq_eval1 = models.IntegerField(null=True, blank=True, verbose_name='Cuello Eval1 - Rotación Izq (°)')
    cuello_rotacion_der_eval1 = models.IntegerField(null=True, blank=True, verbose_name='Cuello Eval1 - Rotación Der (°)')
    
    # Evaluación 2
    cuello_flexion_eval2 = models.IntegerField(null=True, blank=True, verbose_name='Cuello Eval2 - Flexión (°)')
    cuello_extension_eval2 = models.IntegerField(null=True, blank=True, verbose_name='Cuello Eval2 - Extensión (°)')
    cuello_lateral_izq_eval2 = models.IntegerField(null=True, blank=True, verbose_name='Cuello Eval2 - Lateral Izq (°)')
    cuello_lateral_der_eval2 = models.IntegerField(null=True, blank=True, verbose_name='Cuello Eval2 - Lateral Der (°)')
    cuello_rotacion_izq_eval2 = models.IntegerField(null=True, blank=True, verbose_name='Cuello Eval2 - Rotación Izq (°)')
    cuello_rotacion_der_eval2 = models.IntegerField(null=True, blank=True, verbose_name='Cuello Eval2 - Rotación Der (°)')
    
    class Meta:
        abstract = True
# =============================================================================
# MODELO PRINCIPAL EXPEDIENTE
# =============================================================================
class Expediente(models.Model):
    """Expediente principal del paciente"""
    paciente = models.OneToOneField(
        Patient, on_delete=models.CASCADE, related_name='expediente', verbose_name='Paciente'
    )
    numero_expediente = models.CharField(max_length=20, unique=True, verbose_name='Número de expediente')
    
    ESTADO_EXPEDIENTE = [
        ('ACTIVO', 'En tratamiento'),
        ('FINALIZADO', 'Tratamiento finalizado'),
        ('PAUSADO', 'Tratamiento pausado'),
        ('ABANDONADO', 'Abandonó tratamiento'),
    ]
    estado = models.CharField(max_length=15, choices=ESTADO_EXPEDIENTE, default='ACTIVO', verbose_name='Estado del tratamiento')
    notas_generales = models.TextField(blank=True, verbose_name='Notas generales del expediente')
    fecha_inicio_tratamiento = models.DateField(null=True, blank=True, verbose_name='Fecha de inicio del tratamiento')
    fecha_fin_tratamiento = models.DateField(null=True, blank=True, verbose_name='Fecha de finalización del tratamiento')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Expediente de Fisioterapia'
        verbose_name_plural = 'Expedientes de Fisioterapia'
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['numero_expediente']),
            models.Index(fields=['paciente']),
            models.Index(fields=['estado']),
        ]
        permissions = [
            ("can_view_full_expediente", "Puede ver expediente completo"),
            ("can_edit_expediente", "Puede editar expediente"),
        ]

    def __str__(self):
        return f"Exp. {self.numero_expediente} - {self.paciente}"

    def save(self, *args, **kwargs):
        if not self.numero_expediente:
            year = timezone.now().year
            last_exp = Expediente.objects.filter(
                numero_expediente__startswith=f'EXP-FIS-{year}'
            ).order_by('-numero_expediente').first()
            last_number = int(last_exp.numero_expediente.split('-')[-1]) + 1 if last_exp else 1
            self.numero_expediente = f'EXP-FIS-{year}-{last_number:05d}'
        super().save(*args, **kwargs)

    @property
    def tiene_primera_consulta(self):
        return hasattr(self, 'primera_consulta')
    
    @property
    def sesiones_seguimiento(self):
        return self.seguimientos.all().order_by('numero_sesion')
    
    @property
    def total_sesiones(self):
        return self.seguimientos.count()
    
    @property
    def tiene_finalizacion(self):
        return hasattr(self, 'finalizacion')
    
    @property
    def tratamiento_finalizado(self):
        return hasattr(self, 'finalizacion')
# =============================================================================
# 1. PRIMERA CONSULTA - SOLO UNA VEZ POR EXPEDIENTE
# =============================================================================
class PrimeraConsulta(BaseEvaluacionDolor, BaseEvaluacionMuscular, BaseEvaluacionGoniometrica):
    """Evaluación inicial del paciente - Se crea UNA SOLA VEZ"""
    
    TIPO_SANGRE_CHOICES = [
        ('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'), ('O+', 'O+'), ('O-', 'O-'),
    ]
    
    # Relaciones
    expediente = models.OneToOneField(
        Expediente, on_delete=models.CASCADE, related_name='primera_consulta', verbose_name='Expediente'
    )
    profesional = models.ForeignKey(
        CustomUser, on_delete=models.PROTECT, related_name='primeras_consultas',
        limit_choices_to={'tipo_usuario__in': ['FISIO', 'MEDIC']}, verbose_name='Profesional tratante'
    )
    cita = models.OneToOneField(
        'citas.Cita',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='primera_consulta',
        verbose_name='Cita asociada'
    )
    fecha_consulta = models.DateTimeField(default=timezone.now, verbose_name='Fecha de consulta')
    
    # Datos básicos del paciente
    peso = models.FloatField(null=True, blank=True, verbose_name='Peso (kg)')
    estatura = models.FloatField(null=True, blank=True, verbose_name='Estatura (cm)')
    tipo_sangre = models.CharField(max_length=3, choices=TIPO_SANGRE_CHOICES, blank=True, verbose_name='Tipo de sangre')

    # Motivo y diagnóstico
    motivo_consulta = models.TextField(verbose_name='Motivo de consulta')
    tiempo_evolucion = models.CharField(max_length=100, blank=True, verbose_name='Tiempo de evolución')
    mecanismo_lesion = models.TextField(blank=True, verbose_name='Mecanismo de lesión')
    tratamientos_previos = models.TextField(blank=True, verbose_name='Tratamientos previos')

    # ==================== ANTECEDENTES PATOLÓGICOS Y HEREDOPERSONALES ====================
    diabetes = models.TextField(blank=True, verbose_name='Diabetes')
    alergias = models.TextField(blank=True, verbose_name='Alergias')
    hipertension = models.TextField(blank=True, verbose_name='Hipertensión')
    cancer = models.TextField(blank=True, verbose_name='Cáncer')
    traumatismos_previos = models.TextField(blank=True, verbose_name='Traumatismos previos')
    cirugias_previas = models.TextField(blank=True, verbose_name='Cirugías previas')
    transfusiones_sanguineas = models.TextField(blank=True, verbose_name='Transfusiones sanguíneas')
    enf_reumaticas = models.TextField(blank=True, verbose_name='Enfermedades reumáticas')
    accidentes = models.TextField(blank=True, verbose_name='Accidentes')
    cardiopatias = models.TextField(blank=True, verbose_name='Cardiopatías')
    fracturas = models.TextField(blank=True, verbose_name='Fracturas')
    espasmos_o_contracturas = models.TextField(blank=True, verbose_name='Espasmos o contracturas musculares')
    
    # Campos especiales
    signos_vitales = models.TextField(blank=True, verbose_name='Signos vitales', help_text='T/A.. TEMP.. FC.. FR..')
    condiciones_medicas = models.TextField(blank=True, verbose_name='Condiciones médicas adicionales')
    antecedentes_traumatologicos = models.TextField(blank=True, verbose_name='Antecedentes traumatológicos')
    antecedentes_quirurgicos = models.TextField(blank=True, verbose_name='Antecedentes quirúrgicos')
    enfermedades_cronicas = models.TextField(blank=True, verbose_name='Enfermedades crónicas')
    medicacion_actual = models.TextField(blank=True, verbose_name='Medicación actual')

    # ==================== HÁBITOS DE SALUD ====================
    actividad_fisica = models.CharField(max_length=200, blank=True, verbose_name='Actividad física')
    consumo_tabaco = models.CharField(max_length=200, blank=True, verbose_name='Consumo de tabaco')
    consumo_alcohol = models.CharField(max_length=200, blank=True, verbose_name='Consumo de alcohol')
    consumo_drogas = models.CharField(max_length=200, blank=True, verbose_name='Consumo de drogas')
    automedicacion = models.CharField(max_length=200, blank=True, verbose_name='Automedicación')
    esta_embarazada = models.CharField(max_length=200, blank=True, verbose_name='¿Está embarazada?')
    
    pasatiempos = models.CharField(max_length=200, blank=True, verbose_name='Pasatiempos')
    estado_ingravidez = models.CharField(max_length=200, blank=True, verbose_name='Estado de ingravidez')
    cuantos_hijos_tiene = models.PositiveIntegerField(null=True, blank=True, verbose_name='Número de hijos')

    # Diagnostico Medico en Rehabilitacion
    reflejos = models.TextField(blank=True, verbose_name='Reflejos')
    sensibilidad = models.TextField(blank=True, verbose_name='Sensibilidad')
    Lenguaje_orientacion = models.TextField(blank=True, verbose_name='Lenguaje y orientación')
    otros_diagnosticos = models.TextField(blank=True, verbose_name='Otros diagnósticos médicos')

    # Evaluación del dolor inicial (campos adicionales específicos)
    nivel_dolor_inicial = models.IntegerField(choices=BaseEvaluacionDolor.NIVEL_DOLOR, verbose_name='Nivel de dolor inicial')
    tipo_dolor = models.CharField(max_length=100, blank=True, verbose_name='Tipo de dolor')
    factores_agravantes = models.TextField(blank=True, verbose_name='Factores que agravan el dolor')
    factores_atenuantes = models.TextField(blank=True, verbose_name='Factores que alivian el dolor')
    
    # Diagnóstico y plan
    diagnostico_fisioterapia = models.TextField(verbose_name='Diagnóstico fisioterapéutico')
    objetivos_tratamiento = models.TextField(blank=True, verbose_name='Objetivos del tratamiento')
    plan_tratamiento = models.TextField(blank=True, verbose_name='Plan de acción')
    frecuencia_sesiones = models.CharField(max_length=100, blank=True, verbose_name='Frecuencia de sesiones recomendada')
    numero_sesiones_recomendadas = models.PositiveIntegerField(null=True, blank=True, verbose_name='Número de sesiones recomendadas')
    
    # Nota clínica
    nota_subjetivo = models.TextField(blank=True, verbose_name='Subjetivo')
    nota_analisis = models.TextField(blank=True, verbose_name='Análisis')
    nota_observacion = models.TextField(blank=True, verbose_name='Observación')
    
    # Archivos adjuntos
    imagen_lesion = models.ImageField(upload_to='expedientes/primera_consulta/', blank=True, null=True, verbose_name='Imagen de la lesión')
    estudios_complementarios = models.FileField(upload_to='expedientes/estudios/', blank=True, null=True, verbose_name='Estudios complementarios')
    
    # Metadatos
    observaciones = models.TextField(blank=True, verbose_name='Observaciones adicionales')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Primera Consulta'
        verbose_name_plural = 'Primeras Consultas'
    
    def __str__(self):
        return f"Primera Consulta - {self.expediente.paciente} - {self.fecha_consulta.date()}"
    
    def save(self, *args, **kwargs):
        if not self.pk:
            if not self.expediente.fecha_inicio_tratamiento:
                self.expediente.fecha_inicio_tratamiento = self.fecha_consulta.date()
                self.expediente.save(update_fields=['fecha_inicio_tratamiento'])
        super().save(*args, **kwargs)

# =============================================================================
# 2. CONSULTA DE SEGUIMIENTO - MÚLTIPLES SESIONES
# =============================================================================
class ConsultaSegumiento(BaseEvaluacionDolor, BaseEvaluacionMuscular, BaseEvaluacionGoniometrica):
    """Sesiones de seguimiento - Se pueden crear MÚLTIPLES registros"""
    
    # Relaciones
    expediente = models.ForeignKey(
        Expediente, on_delete=models.CASCADE, related_name='seguimientos', verbose_name='Expediente'
    )
    profesional = models.ForeignKey(
        CustomUser, on_delete=models.PROTECT, related_name='seguimientos',
        limit_choices_to={'tipo_usuario__in': ['FISIO', 'MEDIC']}, verbose_name='Profesional tratante'
    )
    cita = models.ForeignKey(
        'citas.Cita',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='seguimientos',
        verbose_name='Cita asociada'
    )
    fecha_consulta = models.DateTimeField(default=timezone.now, verbose_name='Fecha de consulta')
    numero_sesion = models.PositiveIntegerField(verbose_name='Número de sesión')
    
    # Evaluación del progreso en ESTA sesión
    nivel_dolor_actual = models.IntegerField(choices=BaseEvaluacionDolor.NIVEL_DOLOR, verbose_name='Nivel de dolor actual')
    evolucion_paciente = models.TextField(verbose_name='Evolución desde última sesión')
    respuesta_tratamiento = models.TextField(blank=True, verbose_name='Respuesta al tratamiento')
    
    # Tratamiento aplicado en ESTA sesión
    tecnicas_aplicadas = models.TextField(verbose_name='Técnicas aplicadas')
    ejercicios_realizados = models.TextField(blank=True, verbose_name='Ejercicios realizados')
    duracion_sesion = models.PositiveIntegerField(null=True, blank=True, verbose_name='Duración (minutos)')
    
    # Reevaluación
    reevaluacion_rango_movimiento = models.TextField(blank=True, verbose_name='Reevaluación ROM')
    
    # Tratamiento realizado en esta sesión
    tratamiento_realizado = models.TextField(blank=True, verbose_name='Tratamiento realizado en esta sesión')
    
    # Observaciones y plan
    observaciones = models.TextField(blank=True, verbose_name='Observaciones')
    plan_proxima_sesion = models.TextField(blank=True, verbose_name='Plan para próxima sesión')
    imagen_evolucion = models.ImageField(upload_to='expedientes/evolucion/', blank=True, null=True, verbose_name='Imagen de evolución')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Consulta de Seguimiento'
        verbose_name_plural = 'Consultas de Seguimiento'
        ordering = ['expediente', 'numero_sesion']
        unique_together = [['expediente', 'numero_sesion']]
    
    def __str__(self):
        return f"Sesión {self.numero_sesion} - {self.expediente.paciente} - {self.fecha_consulta.date()}"
    
    def save(self, *args, **kwargs):
        if self.pk is None:
            ultima_sesion = ConsultaSegumiento.objects.filter(
                expediente=self.expediente
            ).order_by('-numero_sesion').first()
            self.numero_sesion = (ultima_sesion.numero_sesion + 1) if ultima_sesion else 1
        super().save(*args, **kwargs)
    
    @property
    def porcentaje_mejoria(self):
        if hasattr(self.expediente, 'primera_consulta'):
            dolor_inicial = self.expediente.primera_consulta.nivel_dolor_inicial
            if dolor_inicial and self.nivel_dolor_actual:
                mejoria = dolor_inicial - self.nivel_dolor_actual
                return round((mejoria / dolor_inicial) * 100, 2)
        return None
# =============================================================================
# 3. CONSULTA DE FINALIZACIÓN - SOLO UNA VEZ POR EXPEDIENTE
# =============================================================================
class ConsultaFinalizacion(BaseEvaluacionDolor, BaseEvaluacionMuscular, BaseEvaluacionGoniometrica):
    """Alta del paciente y plan de ejercicios - Se crea UNA SOLA VEZ"""
    
    MOTIVOS_FINALIZACION = [
        ('ALTA', 'Alta por mejoría completa'),
        ('MEJORIA', 'Mejoría significativa pero no completa'),
        ('NO_MEJORIA', 'No mejoría o empeoramiento'),
        ('RENUNCIA', 'Renuncia voluntaria del paciente'),
        ('TRASLADO', 'Traslado a otro centro o profesional'),
        ('FALLECIMIENTO', 'Fallecimiento del paciente'),
    ]
    # Relaciones
    expediente = models.OneToOneField(
        Expediente, on_delete=models.CASCADE, related_name='finalizacion', verbose_name='Expediente'
    )
    profesional = models.ForeignKey(
        CustomUser, on_delete=models.PROTECT, related_name='finalizaciones',
        limit_choices_to={'tipo_usuario__in': ['FISIO', 'MEDIC']}, verbose_name='Profesional tratante'
    )
    cita = models.OneToOneField(
        'citas.Cita',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='finalizacion',
        verbose_name='Cita asociada'
    )
    fecha_consulta = models.DateTimeField(default=timezone.now, verbose_name='Fecha de consulta')
    
    # Datos de finalizacion tratamiento
    motivos_finalizacion = models.CharField(max_length=20, choices=MOTIVOS_FINALIZACION, verbose_name='Motivos de finalización')
    
    # Evaluación final
    nivel_dolor_final = models.IntegerField(choices=BaseEvaluacionDolor.NIVEL_DOLOR, verbose_name='Nivel de dolor final')
    
    # Resumen del tratamiento
    descripcion_tratamiento = models.TextField(blank=True, verbose_name='Descripción del tratamiento realizado')
    objetivos_alcanzados = models.TextField(verbose_name='Objetivos alcanzados')
    recomendaciones_finales = models.TextField(blank=True, verbose_name='Recomendaciones finales')
    observaciones = models.TextField(blank=True, null=True, verbose_name='Observaciones adicionales')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Consulta de Finalización'
        verbose_name_plural = 'Consultas de Finalización'
    
    def __str__(self):
        return f"Finalización - {self.expediente.paciente} - {self.fecha_consulta.date()}"
    
    def save(self, *args, **kwargs):
        self.expediente.estado = 'FINALIZADO'
        self.expediente.fecha_fin_tratamiento = self.fecha_consulta.date()
        self.expediente.save(update_fields=['estado', 'fecha_fin_tratamiento'])
        super().save(*args, **kwargs)