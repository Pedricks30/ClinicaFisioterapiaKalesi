from django.conf import settings
from django.db import models
from django.urls import reverse

class Notificacion(models.Model):
    TIPOS = (
        ('primary', 'Primaria'),
        ('success', 'Éxito'),
        ('danger', 'Urgente'),
        ('warning', 'Advertencia'),
    )

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # Usa el CustomUser configurado
        on_delete=models.CASCADE, 
        related_name='notificaciones'
    )
    mensaje = models.CharField(max_length=255)
    leida = models.BooleanField(default=False)
    tipo = models.CharField(max_length=20, choices=TIPOS, default='primary')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    url = models.CharField(max_length=200, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-fecha_creacion']
        verbose_name = 'Notificación'
        verbose_name_plural = 'Notificaciones'

    def __str__(self):
        return f"Notificación para {self.usuario.username}: {self.mensaje[:50]}..."
    
    def get_absolute_url(self):
        return self.url or reverse('ver_notificaciones')
    
    def marcar_como_leida(self):
        self.leida = True
        self.save()