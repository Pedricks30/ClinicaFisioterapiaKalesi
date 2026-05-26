from datetime import datetime, timedelta
from django.db import models
from django.apps import apps
from users.models import CustomUser

from django.core.exceptions import ValidationError


class Horario(models.Model):
    DIAS_SEMANA = [
        ('LUN', 'Lunes'),
        ('MAR', 'Martes'),
        ('MIE', 'Miércoles'),
        ('JUE', 'Jueves'),
        ('VIE', 'Viernes'),
        ('SAB', 'Sábado'),
        ('DOM', 'Domingo'),
    ]
    
    # Relación con el profesional (Médico o Fisioterapeuta)
    profesional = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='horarios_profesional',
        limit_choices_to={'tipo_usuario__in': ['MEDIC', 'FISIO']},
        verbose_name='Profesional'
    )
    
    dias_semana = models.CharField(
        max_length=100,
        verbose_name='Días de la semana',
        help_text='Días separados por coma: LUN,MAR,MIE'
    )
    
    hora_inicio = models.TimeField(verbose_name='Hora de inicio')
    hora_fin = models.TimeField(verbose_name='Hora de fin')
    disponible = models.BooleanField(default=True, verbose_name='¿Disponible?')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Horario'
        verbose_name_plural = 'Horarios'
        # ELIMINAMOS el UniqueConstraint de profesional
        ordering = ['profesional', 'hora_inicio', 'dias_semana']
    
    def clean(self):
        """Validación personalizada para evitar solapamientos de horarios"""
        if self.hora_inicio and self.hora_fin:
            if self.hora_inicio >= self.hora_fin:
                raise ValidationError('La hora de inicio debe ser anterior a la hora de fin.')
            
            # Validar duración mínima de 15 minutos
            hoy = datetime.now().date()
            inicio_dt = datetime.combine(hoy, self.hora_inicio)
            fin_dt = datetime.combine(hoy, self.hora_fin)
            if (fin_dt - inicio_dt) < timedelta(minutes=15):
                raise ValidationError('El horario debe tener al menos 15 minutos de duración.')
        
        # Validar solapamiento con otros horarios del mismo profesional
        if self.profesional_id and self.dias_semana:
            dias_seleccionados = self.dias_semana.split(',')
            horarios_existentes = Horario.objects.filter(
                profesional=self.profesional,
                disponible=True
            ).exclude(pk=self.pk)
            
            for horario in horarios_existentes:
                dias_existentes = horario.dias_semana.split(',')
                dias_comunes = set(dias_seleccionados) & set(dias_existentes)
                
                if dias_comunes:
                    # Verificar si hay solapamiento de horas
                    if (self.hora_inicio < horario.hora_fin and 
                        self.hora_fin > horario.hora_inicio):
                        dias_str = ', '.join([dict(self.DIAS_SEMANA)[d] for d in dias_comunes])
                        raise ValidationError(
                            f'El horario solapa con otro existente en los días: {dias_str}. '
                            f'Horario existente: {horario.hora_inicio} - {horario.hora_fin}'
                        )
    
    def save(self, *args, **kwargs):
        self.full_clean()  # Ejecutar validaciones antes de guardar
        super().save(*args, **kwargs)
    
    def get_dias_display(self):
        """Devuelve lista con nombres completos de los días"""
        dias = self.dias_semana.split(',')
        return [dict(self.DIAS_SEMANA).get(dia, dia) for dia in dias]
    
    def __str__(self):
        dias = ", ".join(self.get_dias_display())
        estado = "✓" if self.disponible else "✗"
        return f"{self.profesional.get_full_name()} - {dias} {self.hora_inicio}-{self.hora_fin} {estado}"
    
    @property
    def especialidad_profesional(self):
        """
        Obtiene la especialidad del profesional desde su perfil (Medico o Fisioterapeuta).
        """
        perfil = self.profesional.perfil_profesional
        if perfil and perfil.specialties:
            return perfil.specialties
        return None
    
    @property
    def tipo_profesional(self):
        """Retorna 'Médico' o 'Fisioterapeuta'"""
        return self.profesional.get_tipo_usuario_display()
    
    @classmethod
    def generar_horarios_disponibles(cls, profesional, fecha):
        """Genera horarios disponibles para un profesional en una fecha específica"""
        weekday_map = {
            0: 'LUN', 1: 'MAR', 2: 'MIE', 3: 'JUE',
            4: 'VIE', 5: 'SAB', 6: 'DOM'
        }
        dia_actual = weekday_map[fecha.weekday()]
        
        # Obtener TODOS los horarios del profesional para ese día
        horarios = cls.objects.filter(
            profesional=profesional,
            dias_semana__contains=dia_actual,
            disponible=True
        ).order_by('hora_inicio')
        
        # Usar apps.get_model para evitar importación circular
        Cita = apps.get_model('citas', 'Cita')
        citas_existentes = Cita.objects.filter(
            profesional=profesional,
            fecha__date=fecha,
            estado__in=['PENDIENTE', 'CONFIRMADA']
        )
        
        horarios_disponibles = []
        for horario in horarios:
            inicio = datetime.combine(fecha, horario.hora_inicio)
            fin = datetime.combine(fecha, horario.hora_fin)
            
            colision = False
            for cita in citas_existentes:
                cita_inicio = cita.fecha
                cita_fin = cita.fecha + timedelta(minutes=cita.duracion)
                if (inicio < cita_fin) and (fin > cita_inicio):
                    colision = True
                    break
            
            if not colision:
                horarios_disponibles.append({
                    'inicio': inicio,
                    'fin': fin,
                    'horario_id': horario.id
                })
        
        return horarios_disponibles