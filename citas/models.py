from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from datetime import timedelta
from django.core.exceptions import ValidationError
from paciente.models import Patient
from users.models import CustomUser
from horario.models import Horario


class Cita(models.Model):
    # Estados de la cita
    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('CONFIRMADA', 'Confirmada'),
        ('EN_PROCESO', 'En Proceso'),
        ('COMPLETADA', 'Completada'),
        ('CANCELADA', 'Cancelada'),
        ('REPROGRAMADA', 'Reprogramada'),
        ('NO_ASISTIO', 'No Asistió'),
    ]
    
    # Tipos de cita específicos para fisioterapia
    TIPO_CITA_FISIOTERAPIA = [
        ('PRIMERA_CONSULTA', 'Primera Consulta - Evaluación Inicial'),
        ('SEGUIMIENTO', 'Seguimiento - Sesión de Tratamiento'),
        ('FINALIZACION', 'Finalización - Alta del Paciente'),
        ('REVISION', 'Revisión - Control Post-Alta'),
        ('OTRO', 'Otro tipo de consulta'),
    ]
    
    # Relaciones principales
    paciente = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='citas_paciente',
        verbose_name='Paciente'
    )
    profesional = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='citas_profesional',
        limit_choices_to={'tipo_usuario__in': ['MEDIC', 'FISIO']},
        verbose_name='Profesional'
    )
    
    # Información de la cita
    fecha = models.DateTimeField(
        verbose_name='Fecha y hora de la cita'
    )
    duracion = models.PositiveIntegerField(
        default=30,
        help_text="Duración en minutos"
    )
    motivo = models.TextField(
        verbose_name='Motivo de la cita'
    )
    
    # Estado y tipo de cita
    estado = models.CharField(
        max_length=15,
        choices=ESTADO_CHOICES,
        default='PENDIENTE',
        verbose_name='Estado de la cita'
    )
    tipo_cita = models.CharField(
        max_length=20,
        choices=TIPO_CITA_FISIOTERAPIA,
        default='OTRO',
        verbose_name='Tipo de cita',
        help_text='Clasificación de la cita según el tratamiento de fisioterapia'
    )
    
    # Número de sesión (para seguimiento de tratamiento)
    numero_sesion = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name='Número de sesión',
        help_text='Número de sesión dentro del tratamiento (1, 2, 3, etc.)'
    )
    
    # Quién creó la cita
    creada_por = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name='citas_creadas',
        limit_choices_to={'tipo_usuario__in': ['RECEP', 'ADMIN', 'MEDIC', 'FISIO']},
        verbose_name='Creada por'
    )
    
    # Relación con horario del profesional
    horario = models.ForeignKey(
        Horario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='citas',
        help_text="Horario profesional asociado a esta cita"
    )
    
    # Notas adicionales
    notas_internas = models.TextField(
        blank=True,
        verbose_name='Notas internas',
        help_text='Notas visibles solo para el personal'
    )
    notas_paciente = models.TextField(
        blank=True,
        verbose_name='Notas para el paciente',
        help_text='Instrucciones o notas visibles para el paciente'
    )
    
    # Recordatorios
    recordatorio_enviado = models.BooleanField(
        default=False,
        verbose_name='¿Recordatorio enviado?'
    )
    fecha_recordatorio = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Fecha de envío del recordatorio'
    )
    
    # Confirmación del paciente
    confirmada_paciente = models.BooleanField(
        default=False,
        verbose_name='¿Confirmada por el paciente?'
    )
    fecha_confirmacion = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Fecha de confirmación'
    )
    
    # Metadatos
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Cita'
        verbose_name_plural = 'Citas'
        ordering = ['-fecha']
        indexes = [
            models.Index(fields=['profesional', 'fecha']),
            models.Index(fields=['paciente', 'fecha']),
            models.Index(fields=['estado']),
            models.Index(fields=['tipo_cita']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['profesional', 'fecha'],
                name='unique_profesional_fecha',
                condition=models.Q(estado__in=['PENDIENTE', 'CONFIRMADA', 'EN_PROCESO'])
            ),
        ]
        permissions = [
            ("can_manage_citas", "Puede gestionar todas las citas"),
            ("can_confirm_citas", "Puede confirmar citas"),
            ("can_cancel_citas", "Puede cancelar citas"),
        ]
    
    def __str__(self):
        tipo = dict(self.TIPO_CITA_FISIOTERAPIA).get(self.tipo_cita, '')
        return f"Cita #{self.id} - {self.paciente} ({tipo}) - {self.fecha.strftime('%d/%m/%Y %H:%M')}"
    
    def clean(self):
        """Validaciones adicionales para el modelo"""
        super().clean()
        
        # Validación de duración mínima
        if self.duracion < 15:
            raise ValidationError({
                'duracion': 'La duración mínima de una cita es de 15 minutos'
            })
        
        # Validación de que la duración sea múltiplo de 15 minutos
        if self.duracion % 15 != 0:
            raise ValidationError({
                'duracion': 'La duración debe ser un múltiplo de 15 minutos'
            })
        
        # Validación de duración máxima (4 horas)
        if self.duracion > 240:
            raise ValidationError({
                'duracion': 'La duración máxima de una cita es de 4 horas'
            })
        
        # Validación de fecha no pasada para citas nuevas
        if not self.pk and self.fecha < timezone.now():
            raise ValidationError({
                'fecha': 'No se pueden agendar citas en fechas pasadas'
            })
        
        # Validación de solapamiento para citas activas
        if self.estado in ['PENDIENTE', 'CONFIRMADA', 'EN_PROCESO']:
            self.validar_solapamiento()
        
        # Validación de horario profesional
        if self.horario and self.horario.profesional != self.profesional:
            raise ValidationError({
                'horario': 'El horario seleccionado no corresponde al profesional'
            })
        
        # Validación de tipo de cita según el estado del expediente
        if self.tipo_cita == 'PRIMERA_CONSULTA':
            self.validar_primera_consulta()
        elif self.tipo_cita == 'FINALIZACION':
            self.validar_finalizacion()
    
    def validar_solapamiento(self):
        """Valida que no haya citas solapadas para el mismo profesional"""
        inicio_cita = self.fecha
        fin_cita = self.fecha + timedelta(minutes=self.duracion)
        
        citas_solapadas = Cita.objects.filter(
            profesional=self.profesional,
            fecha__lt=fin_cita,
            fecha__gt=inicio_cita - timedelta(minutes=self.duracion),
            estado__in=['PENDIENTE', 'CONFIRMADA', 'EN_PROCESO']
        )
        
        if self.pk:
            citas_solapadas = citas_solapadas.exclude(pk=self.pk)
        
        if citas_solapadas.exists():
            cita_conflicto = citas_solapadas.first()
            raise ValidationError(
                f'El profesional ya tiene una cita programada que se solapa con este horario. '
                f'Conflicto con: {cita_conflicto}'
            )
    
    def validar_primera_consulta(self):
        """Valida que no exista otra primera consulta para el mismo paciente"""
        from expedientes.models import Expediente
        
        # Verificar si ya existe un expediente con primera consulta
        try:
            expediente = Expediente.objects.get(paciente=self.paciente)
            if expediente.primera_consulta_realizada:
                # Permitir solo si esta es la cita asociada a esa primera consulta
                from expedientes.models import HistoriaClinicaFisioterapia
                if not HistoriaClinicaFisioterapia.objects.filter(
                    cita=self,
                    tipo_historia='PRIMERA_CONSULTA'
                ).exists():
                    raise ValidationError({
                        'tipo_cita': 'Este paciente ya tiene una primera consulta registrada'
                    })
        except Expediente.DoesNotExist:
            pass  # Si no tiene expediente, es su primera consulta
    
    def validar_finalizacion(self):
        """Valida que existan sesiones previas antes de una finalización"""
        from expedientes.models import Expediente, HistoriaClinicaFisioterapia
        
        try:
            expediente = Expediente.objects.get(paciente=self.paciente)
            
            # Verificar que tenga al menos una sesión de seguimiento
            sesiones_seguimiento = HistoriaClinicaFisioterapia.objects.filter(
                expediente=expediente,
                tipo_historia='SEGUIMIENTO'
            ).count()
            
            if sesiones_seguimiento == 0:
                raise ValidationError({
                    'tipo_cita': 'Debe existir al menos una sesión de seguimiento antes de programar una finalización'
                })
            
            # Verificar que no exista ya una finalización
            if expediente.tratamiento_finalizado:
                # Permitir solo si esta es la cita asociada a esa finalización
                if not HistoriaClinicaFisioterapia.objects.filter(
                    cita=self,
                    tipo_historia='FINALIZACION'
                ).exists():
                    raise ValidationError({
                        'tipo_cita': 'Este paciente ya tiene un tratamiento finalizado'
                    })
                    
        except Expediente.DoesNotExist:
            raise ValidationError({
                'tipo_cita': 'El paciente no tiene un expediente activo'
            })
    
    @property
    def hora_inicio(self):
        """Hora de inicio de la cita"""
        return self.fecha.time()
    
    @property
    def hora_fin(self):
        """Hora de finalización de la cita"""
        return (self.fecha + timedelta(minutes=self.duracion)).time()
    
    @property
    def fecha_fin(self):
        """Fecha y hora de finalización de la cita"""
        return self.fecha + timedelta(minutes=self.duracion)
    
    @property
    def tiempo_restante(self):
        """Tiempo restante hasta la cita"""
        if self.estado in ['PENDIENTE', 'CONFIRMADA']:
            return self.fecha - timezone.now()
        return None
    
    @property
    def puede_ser_cancelada(self):
        """Determina si la cita puede ser cancelada (24 horas de anticipación)"""
        if self.estado not in ['PENDIENTE', 'CONFIRMADA']:
            return False
        tiempo_restante = self.fecha - timezone.now()
        return tiempo_restante > timedelta(hours=24)
    
    @property
    def puede_ser_reprogramada(self):
        """Determina si la cita puede ser reprogramada (12 horas de anticipación)"""
        if self.estado not in ['PENDIENTE', 'CONFIRMADA']:
            return False
        tiempo_restante = self.fecha - timezone.now()
        return tiempo_restante > timedelta(hours=12)
    
    @property
    def puede_iniciar(self):
        """Determina si la cita puede ser iniciada (30 min antes hasta 15 min después)"""
        if self.estado not in ['CONFIRMADA', 'PENDIENTE']:
            return False
        ahora = timezone.now()
        return (self.fecha - timedelta(minutes=30)) <= ahora <= (self.fecha + timedelta(minutes=15))
    
    @property
    def es_primera_consulta(self):
        """Verifica si es una cita de primera consulta"""
        return self.tipo_cita == 'PRIMERA_CONSULTA'
    
    @property
    def es_seguimiento(self):
        """Verifica si es una cita de seguimiento"""
        return self.tipo_cita == 'SEGUIMIENTO'
    
    @property
    def es_finalizacion(self):
        """Verifica si es una cita de finalización"""
        return self.tipo_cita == 'FINALIZACION'
    
    @property
    def es_revision(self):
        """Verifica si es una cita de revisión post-alta"""
        return self.tipo_cita == 'REVISION'
    
    def confirmar(self, usuario=None):
        """Confirma la cita"""
        if self.estado not in ['PENDIENTE']:
            raise ValidationError('Solo se pueden confirmar citas pendientes')
        
        self.estado = 'CONFIRMADA'
        if usuario:
            self.confirmada_paciente = True
            self.fecha_confirmacion = timezone.now()
        self.save()
        self.enviar_notificacion('confirmacion')
    
    def iniciar(self, usuario):
        """Marca la cita como en proceso"""
        if not self.puede_iniciar:
            raise ValidationError('La cita no puede ser iniciada en este momento')
        
        self.estado = 'EN_PROCESO'
        self.save()
    
    def completar(self, usuario):
        """Marca la cita como completada"""
        if self.estado != 'EN_PROCESO':
            raise ValidationError('Solo se pueden completar citas en proceso')
        
        self.estado = 'COMPLETADA'
        self.save()
    
    def cancelar(self, usuario, motivo_cancelacion=None):
        """Cancela la cita"""
        if not self.puede_ser_cancelada:
            raise ValidationError(
                'La cita no puede ser cancelada. '
                'El tiempo mínimo para cancelar es de 24 horas antes.'
            )
        
        self.estado = 'CANCELADA'
        self.save()
        
        # Registrar el motivo en el histórico
        CitaHistorico.objects.create(
            cita_original=self,
            fecha_original=self.fecha,
            fecha_cambio=timezone.now(),
            motivo=motivo_cancelacion or f"Cancelada por {usuario.get_full_name()}",
            usuario=usuario,
            tipo_cambio='CANCELACION'
        )
        
        self.enviar_notificacion('cancelacion')
    
    def reprogramar(self, nueva_fecha, usuario, motivo_reprogramacion=None):
        """Reprograma la cita para una nueva fecha"""
        if not self.puede_ser_reprogramada:
            raise ValidationError(
                'La cita no puede ser reprogramada. '
                'El tiempo mínimo para reprogramar es de 12 horas antes.'
            )
        
        fecha_anterior = self.fecha
        
        # Actualizar la cita
        self.fecha = nueva_fecha
        self.estado = 'REPROGRAMADA'
        self.save()
        
        # Crear registro histórico
        CitaHistorico.objects.create(
            cita_original=self,
            fecha_original=fecha_anterior,
            fecha_cambio=nueva_fecha,
            motivo=motivo_reprogramacion or f"Reprogramada por {usuario.get_full_name()}",
            usuario=usuario,
            tipo_cambio='REPROGRAMACION'
        )
        
        self.enviar_notificacion('reprogramacion')
    
    def marcar_no_asistio(self, usuario, motivo=None):
        """Marca la cita como no asistida"""
        if self.estado not in ['PENDIENTE', 'CONFIRMADA']:
            raise ValidationError('Solo se pueden marcar como no asistidas citas pendientes o confirmadas')
        
        self.estado = 'NO_ASISTIO'
        self.save()
        
        CitaHistorico.objects.create(
            cita_original=self,
            fecha_original=self.fecha,
            fecha_cambio=timezone.now(),
            motivo=motivo or f"No asistió - Registrado por {usuario.get_full_name()}",
            usuario=usuario,
            tipo_cambio='NO_ASISTIO'
        )
        
        self.enviar_notificacion('no_asistio')
    
    def enviar_notificacion(self, tipo):
        """Envía notificaciones por email según el tipo de evento"""
        subject_map = {
            'confirmacion': f"✅ Confirmación de Cita #{self.id} - Clínica de Fisioterapia",
            'recordatorio': f"⏰ Recordatorio de Cita #{self.id} - Mañana",
            'cancelacion': f"❌ Cancelación de Cita #{self.id}",
            'reprogramacion': f"🔄 Reprogramación de Cita #{self.id}",
            'no_asistio': f"⚠️ Registro de Inasistencia - Cita #{self.id}",
        }
        
        template_map = {
            'confirmacion': 'citas/emails/confirmacion.html',
            'recordatorio': 'citas/emails/recordatorio.html',
            'cancelacion': 'citas/emails/cancelacion.html',
            'reprogramacion': 'citas/emails/reprogramacion.html',
            'no_asistio': 'citas/emails/no_asistio.html',
        }
        
        context = {
            'cita': self,
            'tipo': tipo,
            'paciente': self.paciente,
            'profesional': self.profesional,
            'clinica': 'Clínica de Fisioterapia',
            'fecha_actual': timezone.now(),
        }
        
        try:
            # Email para el paciente
            if self.paciente.email:
                html_message = render_to_string(template_map.get(tipo, template_map['confirmacion']), context)
                send_mail(
                    subject=subject_map[tipo],
                    message='',
                    html_message=html_message,
                    from_email='notificaciones@clinicafisioterapia.com',
                    recipient_list=[self.paciente.email],
                    fail_silently=True
                )
            
            # Email para el profesional
            if self.profesional.email:
                context['es_profesional'] = True
                html_message = render_to_string(template_map.get(tipo, template_map['confirmacion']), context)
                send_mail(
                    subject=f"[Profesional] {subject_map[tipo]}",
                    message='',
                    html_message=html_message,
                    from_email='notificaciones@clinicafisioterapia.com',
                    recipient_list=[self.profesional.email],
                    fail_silently=True
                )
                
        except Exception as e:
            # Loggear el error pero no interrumpir el flujo
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error enviando notificación de cita #{self.id}: {str(e)}")
    
    def save(self, *args, **kwargs):
        """Lógica personalizada al guardar"""
        is_new = self.pk is None
        
        # Si es nueva y es primera consulta, asignar número de sesión 1
        if is_new and self.tipo_cita == 'PRIMERA_CONSULTA':
            self.numero_sesion = 1
        
        # Si es seguimiento, calcular automáticamente el número de sesión
        if is_new and self.tipo_cita == 'SEGUIMIENTO':
            ultima_cita = Cita.objects.filter(
                paciente=self.paciente,
                profesional=self.profesional
            ).order_by('-numero_sesion').first()
            
            if ultima_cita and ultima_cita.numero_sesion:
                self.numero_sesion = ultima_cita.numero_sesion + 1
        
        super().save(*args, **kwargs)


@receiver(post_save, sender=Cita)
def manejar_notificaciones_cita(sender, instance, created, **kwargs):
    """
    Maneja las notificaciones automáticas cuando se crea o modifica una cita
    """
    if created:
        # Nueva cita creada
        instance.enviar_notificacion('confirmacion')
    elif instance.estado == 'CANCELADA':
        # Cita cancelada
        instance.enviar_notificacion('cancelacion')
    elif instance.estado == 'REPROGRAMADA':
        # Cita reprogramada
        instance.enviar_notificacion('reprogramacion')


class CitaHistorico(models.Model):
    """
    Registro histórico de cambios en las citas
    """
    TIPO_CAMBIO_CHOICES = [
        ('CREACION', 'Creación'),
        ('CONFIRMACION', 'Confirmación'),
        ('REPROGRAMACION', 'Reprogramación'),
        ('CANCELACION', 'Cancelación'),
        ('COMPLETADA', 'Completada'),
        ('NO_ASISTIO', 'No Asistió'),
        ('MODIFICACION', 'Modificación'),
    ]
    
    cita_original = models.ForeignKey(
        Cita,
        on_delete=models.CASCADE,
        related_name='historico',
        verbose_name='Cita original'
    )
    fecha_original = models.DateTimeField(
        verbose_name='Fecha original'
    )
    fecha_cambio = models.DateTimeField(
        verbose_name='Fecha del cambio'
    )
    tipo_cambio = models.CharField(
        max_length=20,
        choices=TIPO_CAMBIO_CHOICES,
        default='MODIFICACION',
        verbose_name='Tipo de cambio'
    )
    motivo = models.TextField(
        verbose_name='Motivo del cambio'
    )
    usuario = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Usuario que realizó el cambio'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de registro'
    )
    update_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Fecha de actualización'
    )
    
    class Meta:
        verbose_name = 'Histórico de Cita'
        verbose_name_plural = 'Históricos de Citas'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['cita_original']),
            models.Index(fields=['tipo_cambio']),
        ]
    
    def __str__(self):
        return f"{self.get_tipo_cambio_display()} - Cita #{self.cita_original.id}"


def enviar_recordatorios():
    """
    Función para enviar recordatorios de citas.
    Debe ejecutarse como tarea programada (cron job o similar).
    """
    ahora = timezone.now()
    manana = ahora.date() + timedelta(days=1)
    
    # Buscar citas para mañana
    citas = Cita.objects.filter(
        fecha__date=manana,
        estado__in=['PENDIENTE', 'CONFIRMADA'],
        recordatorio_enviado=False
    )
    
    for cita in citas:
        try:
            cita.enviar_notificacion('recordatorio')
            cita.recordatorio_enviado = True
            cita.fecha_recordatorio = ahora
            cita.save(update_fields=['recordatorio_enviado', 'fecha_recordatorio'])
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error enviando recordatorio para cita #{cita.id}: {str(e)}")


# Función para obtener el resumen de citas del día
def get_citas_del_dia(fecha=None):
    """
    Obtiene todas las citas de una fecha específica (por defecto hoy)
    """
    if fecha is None:
        fecha = timezone.now().date()
    
    return Cita.objects.filter(
        fecha__date=fecha,
        estado__in=['PENDIENTE', 'CONFIRMADA', 'EN_PROCESO', 'COMPLETADA']
    ).select_related('paciente', 'profesional').order_by('fecha')


# Función para estadísticas de citas
def get_estadisticas_citas(profesional=None, fecha_inicio=None, fecha_fin=None):
    """
    Obtiene estadísticas de citas para un período y profesional específico
    """
    from django.db.models import Count
    
    queryset = Cita.objects.all()
    
    if profesional:
        queryset = queryset.filter(profesional=profesional)
    
    if fecha_inicio:
        queryset = queryset.filter(fecha__date__gte=fecha_inicio)
    
    if fecha_fin:
        queryset = queryset.filter(fecha__date__lte=fecha_fin)
    
    estadisticas = {
        'total_citas': queryset.count(),
        'citas_completadas': queryset.filter(estado='COMPLETADA').count(),
        'citas_canceladas': queryset.filter(estado='CANCELADA').count(),
        'citas_no_asistidas': queryset.filter(estado='NO_ASISTIO').count(),
        'por_tipo': dict(queryset.values('tipo_cita').annotate(count=Count('id')).values_list('tipo_cita', 'count')),
        'por_estado': dict(queryset.values('estado').annotate(count=Count('id')).values_list('estado', 'count')),
    }
    
    return estadisticas