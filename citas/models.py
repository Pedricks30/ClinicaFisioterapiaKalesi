from django.db import models
from medical.models import MedicalUser
from paciente.models import Patient
from horario.models import Horario
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from datetime import timedelta

class Cita(models.Model):
    ESTADOS = (
        ('P', 'Pendiente'),
        ('C', 'Confirmada'),
        ('A', 'Atendida'),
        ('N', 'Cancelada'),
    )
    paciente = models.ForeignKey(Patient, on_delete=models.CASCADE)
    profesional = models.ForeignKey(MedicalUser, on_delete=models.CASCADE)
    horario = models.ForeignKey(Horario, on_delete=models.CASCADE, null=True, blank=True)
    fecha = models.DateField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    estado = models.CharField(max_length=1, choices=ESTADOS, default='P')
    motivo = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Cita'
        verbose_name_plural = 'Citas'
        ordering = ['fecha', 'hora_inicio']

    def __str__(self):
        return f"Cita {self.id} - {self.paciente} con {self.profesional}"
    
    def enviar_notificacion(self, tipo):
        subject_map = {
            'confirmacion': f"Confirmación de cita #{self.id}",
            'recordatorio': f"Recordatorio de cita #{self.id}",
            'cancelacion': f"Cancelación de cita #{self.id}"
        }
        
        context = {
            'cita': self,
            'tipo': tipo,
            'paciente': self.paciente,
            'profesional': self.profesional
        }
        
        # Email para el paciente
        html_message = render_to_string('citas/email_notificacion.html', context)
        send_mail(
            subject=subject_map[tipo],
            message='',  # Versión de texto plano (opcional)
            html_message=html_message,
            from_email='notificaciones@clinica.com',
            recipient_list=[self.paciente.email],
            fail_silently=False
        )
        
        # Email para el profesional (opcional)
        if self.profesional.email:
            send_mail(
                subject=f"[Profesional] {subject_map[tipo]}",
                message='',
                html_message=html_message,
                from_email='notificaciones@clinica.com',
                recipient_list=[self.profesional.email],
                fail_silently=False
            )

@receiver(post_save, sender=Cita)
def manejar_notificaciones_cita(sender, instance, created, **kwargs):
    if created:
        # Enviar confirmación al crear
        instance.enviar_notificacion('confirmacion')
    elif instance.estado == 'N':
        # Enviar notificación de cancelación
        instance.enviar_notificacion('cancelacion')

# Tarea programada para recordatorios (usar Celery o cron)
def enviar_recordatorios():
    ahora = timezone.now()
    citas = Cita.objects.filter(
        fecha=ahora.date() + timedelta(days=1),  # Citas para mañana
        hora_inicio__hour=ahora.time().hour,     # Aproximadamente 24h antes
        estado__in=['P', 'C']                    # Pendientes o confirmadas
    )
    
    for cita in citas:
        cita.enviar_notificacion('recordatorio')