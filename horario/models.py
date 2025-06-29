from django.db import models
from medical.models import MedicalUser

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
    
    profesional = models.ForeignKey(MedicalUser, on_delete=models.CASCADE, related_name='horarios')
    dias_laborables = models.CharField(max_length=100, help_text="Días separados por comas")
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    activo = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    def get_dias_display(self):
        dias = self.dias_laborables.split(',')
        return [dict(self.DIAS_SEMANA).get(dia, dia) for dia in dias]

    def __str__(self):
        return f"Horario de {self.profesional.name} - {self.dias_laborables} {self.hora_inicio}-{self.hora_fin}"

    class Meta:
        verbose_name = "Horario"
        verbose_name_plural = "Horarios"
        ordering = ['profesional__name', 'hora_inicio']