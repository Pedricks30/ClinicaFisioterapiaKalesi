from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.core.exceptions import ValidationError
from paciente.models import Patient
from users.models import CustomUser
from citas.models import Cita


class Expediente(models.Model):
    """
    Modelo principal del expediente de fisioterapia de un paciente.
    Se crea automáticamente al registrar un nuevo paciente.
    """
    paciente = models.OneToOneField(
        Patient,
        on_delete=models.CASCADE,
        related_name='expediente',
        verbose_name='Paciente'
    )
    
    # Información general del expediente
    numero_expediente = models.CharField(
        max_length=20,
        unique=True,
        verbose_name='Número de expediente',
        help_text='Número único de identificación del expediente'
    )
    
    # Estado del expediente
    ESTADO_EXPEDIENTE = [
        ('ACTIVO', 'En tratamiento'),
        ('FINALIZADO', 'Tratamiento finalizado'),
        ('PAUSADO', 'Tratamiento pausado'),
        ('ABANDONADO', 'Abandonó tratamiento'),
    ]
    estado = models.CharField(
        max_length=15,
        choices=ESTADO_EXPEDIENTE,
        default='ACTIVO',
        verbose_name='Estado del tratamiento'
    )
    
    # Notas generales del expediente
    notas_generales = models.TextField(
        blank=True,
        verbose_name='Notas generales del expediente'
    )
    
    # Resumen del tratamiento
    fecha_inicio_tratamiento = models.DateField(
        null=True,
        blank=True,
        verbose_name='Fecha de inicio del tratamiento'
    )
    fecha_fin_tratamiento = models.DateField(
        null=True,
        blank=True,
        verbose_name='Fecha de finalización del tratamiento'
    )
    
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
        """Genera automáticamente el número de expediente si es nuevo"""
        if not self.numero_expediente:
            year = timezone.now().year
            last_exp = Expediente.objects.filter(
                numero_expediente__startswith=f'EXP-FIS-{year}'
            ).order_by('-numero_expediente').first()
            
            if last_exp:
                last_number = int(last_exp.numero_expediente.split('-')[-1])
                new_number = last_number + 1
            else:
                new_number = 1
            
            self.numero_expediente = f'EXP-FIS-{year}-{new_number:05d}'
        
        super().save(*args, **kwargs)

    @property
    def cantidad_sesiones(self):
        """Total de sesiones realizadas"""
        return self.historias.filter(
            tipo_historia__in=['SEGUIMIENTO', 'FINALIZACION']
        ).count()

    @property
    def sesiones_completadas(self):
        """Sesiones de seguimiento completadas"""
        return self.historias.filter(tipo_historia='SEGUIMIENTO').count()

    @property
    def primera_consulta_realizada(self):
        """Verifica si ya se realizó la primera consulta"""
        return self.historias.filter(tipo_historia='PRIMERA_CONSULTA').exists()

    @property
    def tratamiento_finalizado(self):
        """Verifica si el tratamiento ya fue finalizado"""
        return self.historias.filter(tipo_historia='FINALIZACION').exists()


class HistoriaClinicaFisioterapia(models.Model):
    """
    Modelo para los tres tipos de historias clínicas de fisioterapia:
    1. PRIMERA CONSULTA: Evaluación inicial completa
    2. CONSULTA DE SEGUIMIENTO: Sesiones de tratamiento
    3. CONSULTA DE FINALIZACIÓN: Alta y plan de ejercicios
    """
    TIPO_HISTORIA = [
        ('PRIMERA_CONSULTA', 'Primera Consulta - Evaluación Inicial'),
        ('SEGUIMIENTO', 'Consulta de Seguimiento - Sesión de Tratamiento'),
        ('FINALIZACION', 'Consulta de Finalización - Alta del Paciente'),
    ]
    
    NIVEL_DOLOR = [
        (0, '0 - Sin dolor'),
        (1, '1 - Dolor muy leve'),
        (2, '2 - Dolor leve'),
        (3, '3 - Dolor moderado'),
        (4, '4 - Dolor moderado-alto'),
        (5, '5 - Dolor alto'),
        (6, '6 - Dolor muy alto'),
        (7, '7 - Dolor severo'),
        (8, '8 - Dolor muy severo'),
        (9, '9 - Dolor extremadamente severo'),
        (10, '10 - Máximo dolor imaginable'),
    ]
    
    # Relaciones
    expediente = models.ForeignKey(
        Expediente,
        on_delete=models.CASCADE,
        related_name='historias',
        verbose_name='Expediente'
    )
    cita = models.OneToOneField(
        Cita,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='historia_fisioterapia',
        verbose_name='Cita asociada'
    )
    profesional = models.ForeignKey(
        CustomUser,
        on_delete=models.PROTECT,
        related_name='historias_fisioterapia',
        limit_choices_to={'tipo_usuario__in': ['FISIO', 'MEDIC']},
        verbose_name='Fisioterapeuta tratante'
    )
    
    # Datos comunes a todas las consultas
    tipo_historia = models.CharField(
        max_length=20,
        choices=TIPO_HISTORIA,
        verbose_name='Tipo de consulta'
    )
    fecha_consulta = models.DateTimeField(
        default=timezone.now,
        verbose_name='Fecha de consulta'
    )
    numero_sesion = models.PositiveIntegerField(
        default=1,
        verbose_name='Número de sesión',
        help_text='Número de sesión del tratamiento'
    )
    
    # ============ CAMPOS PARA PRIMERA CONSULTA ============
    # Motivo de consulta
    motivo_consulta = models.TextField(
        blank=True,
        verbose_name='Motivo de consulta',
        help_text='Razón principal por la que el paciente acude a fisioterapia'
    )
    
    # Historia de la condición actual
    tiempo_evolucion = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Tiempo de evolución',
        help_text='¿Desde cuándo presenta el problema?'
    )
    mecanismo_lesion = models.TextField(
        blank=True,
        verbose_name='Mecanismo de lesión',
        help_text='¿Cómo ocurrió la lesión o problema?'
    )
    tratamientos_previos = models.TextField(
        blank=True,
        verbose_name='Tratamientos previos',
        help_text='¿Ha recibido tratamiento anterior para esta condición?'
    )
    
    # Antecedentes médicos relevantes
    antecedentes_traumatologicos = models.TextField(
        blank=True,
        verbose_name='Antecedentes traumatológicos',
        help_text='Fracturas, luxaciones, esguinces previos, etc.'
    )
    antecedentes_quirurgicos = models.TextField(
        blank=True,
        verbose_name='Antecedentes quirúrgicos',
        help_text='Cirugías previas relacionadas'
    )
    enfermedades_cronicas = models.TextField(
        blank=True,
        verbose_name='Enfermedades crónicas',
        help_text='Diabetes, hipertensión, artritis, etc.'
    )
    medicacion_actual = models.TextField(
        blank=True,
        verbose_name='Medicación actual',
        help_text='Medicamentos que toma actualmente'
    )
    
    # Evaluación del dolor inicial
    nivel_dolor_inicial = models.IntegerField(
        choices=NIVEL_DOLOR,
        null=True,
        blank=True,
        verbose_name='Nivel de dolor (Escala EVA)',
        help_text='Escala Visual Analógica del Dolor (0-10)'
    )
    localizacion_dolor = models.TextField(
        blank=True,
        verbose_name='Localización del dolor',
        help_text='¿Dónde duele exactamente?'
    )
    tipo_dolor = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Tipo de dolor',
        help_text='Punzante, quemante, sordo, etc.'
    )
    factores_agravantes = models.TextField(
        blank=True,
        verbose_name='Factores que agravan el dolor',
        help_text='Movimientos, posiciones o actividades que aumentan el dolor'
    )
    factores_atenuantes = models.TextField(
        blank=True,
        verbose_name='Factores que alivian el dolor',
        help_text='Posiciones, medicamentos o acciones que disminuyen el dolor'
    )
    
    # Evaluación física inicial
    inspeccion_visual = models.TextField(
        blank=True,
        verbose_name='Inspección visual',
        help_text='Observaciones sobre postura, deformidades, inflamación, etc.'
    )
    palpacion = models.TextField(
        blank=True,
        verbose_name='Palpación',
        help_text='Hallazgos a la palpación: tensión muscular, puntos gatillo, etc.'
    )
    evaluacion_postural = models.TextField(
        blank=True,
        verbose_name='Evaluación postural',
        help_text='Análisis de la postura del paciente'
    )
    rango_movimiento = models.TextField(
        blank=True,
        verbose_name='Rango de movimiento (ROM)',
        help_text='Evaluación de la movilidad articular'
    )
    fuerza_muscular = models.TextField(
        blank=True,
        verbose_name='Fuerza muscular',
        help_text='Evaluación de la fuerza muscular (Escala Daniels)'
    )
    pruebas_especiales = models.TextField(
        blank=True,
        verbose_name='Pruebas especiales',
        help_text='Resultados de pruebas ortopédicas específicas'
    )
    
    # Diagnóstico fisioterapéutico
    diagnostico_fisioterapia = models.TextField(
        blank=True,
        verbose_name='Diagnóstico fisioterapéutico',
        help_text='Diagnóstico desde la perspectiva de la fisioterapia'
    )
    objetivos_tratamiento = models.TextField(
        blank=True,
        verbose_name='Objetivos del tratamiento',
        help_text='Metas a alcanzar con el tratamiento fisioterapéutico'
    )
    plan_tratamiento = models.TextField(
        blank=True,
        verbose_name='Plan de tratamiento',
        help_text='Descripción general del plan de tratamiento'
    )
    frecuencia_sesiones = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Frecuencia de sesiones recomendada',
        help_text='Ej: 2 veces por semana'
    )
    numero_sesiones_recomendadas = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name='Número de sesiones recomendadas',
        help_text='Cantidad total de sesiones estimadas'
    )
    
    # ============ CAMPOS PARA CONSULTA DE SEGUIMIENTO ============
    # Evaluación del progreso
    nivel_dolor_actual = models.IntegerField(
        choices=NIVEL_DOLOR,
        null=True,
        blank=True,
        verbose_name='Nivel de dolor actual (EVA)',
        help_text='Escala EVA del dolor en esta sesión'
    )
    evolucion_paciente = models.TextField(
        blank=True,
        verbose_name='Evolución del paciente',
        help_text='¿Cómo ha evolucionado desde la última sesión?'
    )
    respuesta_tratamiento = models.TextField(
        blank=True,
        verbose_name='Respuesta al tratamiento',
        help_text='¿Cómo ha respondido al tratamiento aplicado?'
    )
    
    # Tratamiento aplicado en la sesión
    tecnicas_aplicadas = models.TextField(
        blank=True,
        verbose_name='Técnicas aplicadas',
        help_text='Técnicas de fisioterapia utilizadas en esta sesión'
    )
    ejercicios_realizados = models.TextField(
        blank=True,
        verbose_name='Ejercicios realizados',
        help_text='Ejercicios terapéuticos ejecutados en la sesión'
    )
    terapia_manual = models.TextField(
        blank=True,
        verbose_name='Terapia manual',
        help_text='Técnicas de terapia manual aplicadas'
    )
    agentes_fisicos = models.TextField(
        blank=True,
        verbose_name='Agentes físicos',
        help_text='Ultrasonido, electroterapia, calor, frío, etc.'
    )
    duracion_sesion = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name='Duración de la sesión (minutos)',
        help_text='Tiempo total de la sesión en minutos'
    )
    
    # Reevaluación
    reevaluacion_rango_movimiento = models.TextField(
        blank=True,
        verbose_name='Reevaluación ROM',
        help_text='Nuevos hallazgos en rango de movimiento'
    )
    reevaluacion_fuerza = models.TextField(
        blank=True,
        verbose_name='Reevaluación fuerza muscular',
        help_text='Progreso en fuerza muscular'
    )
    reevaluacion_funcional = models.TextField(
        blank=True,
        verbose_name='Reevaluación funcional',
        help_text='Evaluación de actividades funcionales'
    )
    
    # ============ CAMPOS PARA CONSULTA DE FINALIZACIÓN ============
    # Evaluación final
    nivel_dolor_final = models.IntegerField(
        choices=NIVEL_DOLOR,
        null=True,
        blank=True,
        verbose_name='Nivel de dolor final (EVA)',
        help_text='Escala EVA del dolor al finalizar tratamiento'
    )
    objetivos_alcanzados = models.TextField(
        blank=True,
        verbose_name='Objetivos alcanzados',
        help_text='¿Se cumplieron los objetivos del tratamiento?'
    )
    mejorias_observadas = models.TextField(
        blank=True,
        verbose_name='Mejorías observadas',
        help_text='Cambios positivos observados durante el tratamiento'
    )
    limitaciones_residuales = models.TextField(
        blank=True,
        verbose_name='Limitaciones residuales',
        help_text='Limitaciones que aún persisten (si las hay)'
    )
    
    # Plan de alta
    plan_ejercicios_casa = models.TextField(
        blank=True,
        verbose_name='Plan de ejercicios para casa',
        help_text='Ejercicios que el paciente debe realizar en casa'
    )
    frecuencia_ejercicios = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Frecuencia de ejercicios',
        help_text='¿Con qué frecuencia debe realizar los ejercicios?'
    )
    duracion_ejercicios = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Duración de la rutina',
        help_text='Tiempo estimado de la rutina de ejercicios'
    )
    recomendaciones_finales = models.TextField(
        blank=True,
        verbose_name='Recomendaciones finales',
        help_text='Consejos y precauciones post-tratamiento'
    )
    actividades_permitidas = models.TextField(
        blank=True,
        verbose_name='Actividades permitidas',
        help_text='Actividades que el paciente puede realizar'
    )
    actividades_restringidas = models.TextField(
        blank=True,
        verbose_name='Actividades restringidas',
        help_text='Actividades que debe evitar temporalmente'
    )
    seguimiento_recomendado = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Seguimiento recomendado',
        help_text='¿Se recomienda seguimiento? ¿En cuánto tiempo?'
    )
    
    # Evaluación de satisfacción
    satisfaccion_paciente = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Satisfacción del paciente',
        help_text='Nivel de satisfacción con el tratamiento'
    )
    
    # Observaciones generales
    observaciones = models.TextField(
        blank=True,
        verbose_name='Observaciones adicionales'
    )
    
    # Archivos adjuntos (imágenes, estudios, etc.)
    imagen_lesion = models.ImageField(
        upload_to='expedientes/imagenes_lesiones/%Y/%m/',
        blank=True,
        null=True,
        verbose_name='Imagen de la lesión'
    )
    imagen_evolucion = models.ImageField(
        upload_to='expedientes/imagenes_evolucion/%Y/%m/',
        blank=True,
        null=True,
        verbose_name='Imagen de evolución'
    )
    estudios_complementarios = models.FileField(
        upload_to='expedientes/estudios/%Y/%m/',
        blank=True,
        null=True,
        verbose_name='Estudios complementarios',
        help_text='Radiografías, resonancias, etc.'
    )
    archivo_ejercicios = models.FileField(
        upload_to='expedientes/ejercicios/%Y/%m/',
        blank=True,
        null=True,
        verbose_name='Archivo de ejercicios',
        help_text='PDF o imagen con la rutina de ejercicios'
    )
    
    # Metadatos
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Historia Clínica de Fisioterapia'
        verbose_name_plural = 'Historias Clínicas de Fisioterapia'
        ordering = ['-fecha_consulta']
        indexes = [
            models.Index(fields=['expediente', '-fecha_consulta']),
            models.Index(fields=['profesional', '-fecha_consulta']),
            models.Index(fields=['tipo_historia']),
            models.Index(fields=['cita']),
        ]
        permissions = [
            ("can_view_full_history", "Puede ver historia clínica completa"),
            ("can_create_initial_consultation", "Puede crear primera consulta"),
            ("can_finalize_treatment", "Puede finalizar tratamientos"),
        ]

    def __str__(self):
        tipo = dict(self.TIPO_HISTORIA).get(self.tipo_historia, '')
        return f"{tipo} - {self.expediente.paciente} (Sesión {self.numero_sesion})"

    def clean(self):
        """Validaciones personalizadas"""
        super().clean()
        
        # Validar que solo haya una primera consulta por expediente
        if self.tipo_historia == 'PRIMERA_CONSULTA':
            existe_primera = HistoriaClinicaFisioterapia.objects.filter(
                expediente=self.expediente,
                tipo_historia='PRIMERA_CONSULTA'
            ).exclude(pk=self.pk if self.pk else None)
            
            if existe_primera.exists():
                raise ValidationError(
                    'Ya existe una primera consulta para este expediente'
                )
        
        # Validar que no se pueda crear seguimiento sin primera consulta
        if self.tipo_historia in ['SEGUIMIENTO', 'FINALIZACION']:
            if not self.expediente.primera_consulta_realizada:
                raise ValidationError(
                    'Debe realizar la primera consulta antes de crear seguimientos'
                )
        
        # Validar que no se pueda crear finalización si ya existe una
        if self.tipo_historia == 'FINALIZACION':
            existe_finalizacion = HistoriaClinicaFisioterapia.objects.filter(
                expediente=self.expediente,
                tipo_historia='FINALIZACION'
            ).exclude(pk=self.pk if self.pk else None)
            
            if existe_finalizacion.exists():
                raise ValidationError(
                    'Ya existe una consulta de finalización para este expediente'
                )
        
        # Validar campos requeridos según tipo de historia
        if self.tipo_historia == 'PRIMERA_CONSULTA':
            if not self.motivo_consulta:
                raise ValidationError({
                    'motivo_consulta': 'El motivo de consulta es obligatorio en la primera consulta'
                })
            if not self.diagnostico_fisioterapia:
                raise ValidationError({
                    'diagnostico_fisioterapia': 'El diagnóstico es obligatorio en la primera consulta'
                })
        
        if self.tipo_historia == 'SEGUIMIENTO':
            if self.nivel_dolor_actual is None:
                raise ValidationError({
                    'nivel_dolor_actual': 'Debe evaluar el nivel de dolor en cada seguimiento'
                })
            if not self.tecnicas_aplicadas:
                raise ValidationError({
                    'tecnicas_aplicadas': 'Debe registrar las técnicas aplicadas en la sesión'
                })
        
        if self.tipo_historia == 'FINALIZACION':
            if self.nivel_dolor_final is None:
                raise ValidationError({
                    'nivel_dolor_final': 'Debe evaluar el nivel de dolor final'
                })
            if not self.plan_ejercicios_casa:
                raise ValidationError({
                    'plan_ejercicios_casa': 'Debe proporcionar un plan de ejercicios'
                })

    def save(self, *args, **kwargs):
        """Lógica personalizada al guardar"""
        is_new = self.pk is None
        
        # Si es nuevo, actualizar el número de sesión automáticamente
        if is_new:
            if self.tipo_historia == 'PRIMERA_CONSULTA':
                self.numero_sesion = 1
                # Marcar fecha de inicio de tratamiento
                if not self.expediente.fecha_inicio_tratamiento:
                    self.expediente.fecha_inicio_tratamiento = self.fecha_consulta.date()
                    self.expediente.save(update_fields=['fecha_inicio_tratamiento'])
            else:
                # Para seguimientos y finalización, incrementar número de sesión
                ultima_sesion = HistoriaClinicaFisioterapia.objects.filter(
                    expediente=self.expediente
                ).order_by('-numero_sesion').first()
                
                if ultima_sesion:
                    self.numero_sesion = ultima_sesion.numero_sesion + 1
        
        # Si es finalización, actualizar estado del expediente
        if self.tipo_historia == 'FINALIZACION':
            self.expediente.estado = 'FINALIZADO'
            self.expediente.fecha_fin_tratamiento = self.fecha_consulta.date()
            self.expediente.save(update_fields=['estado', 'fecha_fin_tratamiento'])
        
        super().save(*args, **kwargs)

    @property
    def porcentaje_mejoria_dolor(self):
        """Calcula el porcentaje de mejoría del dolor comparando con la primera consulta"""
        if self.tipo_historia in ['SEGUIMIENTO', 'FINALIZACION']:
            primera_consulta = HistoriaClinicaFisioterapia.objects.filter(
                expediente=self.expediente,
                tipo_historia='PRIMERA_CONSULTA'
            ).first()
            
            if primera_consulta and primera_consulta.nivel_dolor_inicial:
                dolor_actual = self.nivel_dolor_actual if self.tipo_historia == 'SEGUIMIENTO' else self.nivel_dolor_final
                if dolor_actual is not None:
                    mejoria = primera_consulta.nivel_dolor_inicial - dolor_actual
                    porcentaje = (mejoria / primera_consulta.nivel_dolor_inicial) * 100
                    return round(max(0, porcentaje), 2)
        return None

    @property
    def es_primera_consulta(self):
        return self.tipo_historia == 'PRIMERA_CONSULTA'

    @property
    def es_seguimiento(self):
        return self.tipo_historia == 'SEGUIMIENTO'

    @property
    def es_finalizacion(self):
        return self.tipo_historia == 'FINALIZACION'


class PlanEjercicios(models.Model):
    """
    Modelo para almacenar los planes de ejercicios detallados
    que se entregan al paciente en la finalización
    """
    historia_finalizacion = models.ForeignKey(
        HistoriaClinicaFisioterapia,
        on_delete=models.CASCADE,
        related_name='planes_ejercicios',
        limit_choices_to={'tipo_historia': 'FINALIZACION'},
        verbose_name='Historia de finalización'
    )
    nombre_ejercicio = models.CharField(
        max_length=200,
        verbose_name='Nombre del ejercicio'
    )
    descripcion = models.TextField(
        verbose_name='Descripción del ejercicio'
    )
    series = models.CharField(
        max_length=50,
        verbose_name='Series',
        help_text='Ej: 3 series'
    )
    repeticiones = models.CharField(
        max_length=50,
        verbose_name='Repeticiones',
        help_text='Ej: 10-12 repeticiones'
    )
    frecuencia_diaria = models.CharField(
        max_length=100,
        verbose_name='Frecuencia diaria',
        help_text='Ej: 2 veces al día'
    )
    duracion = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Duración',
        help_text='Tiempo de mantenimiento del ejercicio'
    )
    imagen_ejercicio = models.ImageField(
        upload_to='expedientes/ejercicios/imagenes/',
        blank=True,
        null=True,
        verbose_name='Imagen del ejercicio'
    )
    video_ejercicio = models.FileField(
        upload_to='expedientes/ejercicios/videos/',
        blank=True,
        null=True,
        verbose_name='Video demostrativo'
    )
    observaciones = models.TextField(
        blank=True,
        verbose_name='Observaciones del ejercicio'
    )
    orden = models.PositiveIntegerField(
        default=1,
        verbose_name='Orden',
        help_text='Orden de ejecución de los ejercicios'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Plan de Ejercicio'
        verbose_name_plural = 'Planes de Ejercicios'
        ordering = ['orden']
        indexes = [
            models.Index(fields=['historia_finalizacion']),
        ]

    def __str__(self):
        return f"Ejercicio: {self.nombre_ejercicio} - Orden {self.orden}"


# Señal para crear expediente automáticamente al crear paciente lo estoy trabajando desde el archivo signals.py para evitar problemas de importación circular
