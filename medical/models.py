from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver
from core.mixins import ImageCompressionMixin, ImageDeletionMixin
from users.models import CustomUser, Specialties

class Medico(ImageCompressionMixin, ImageDeletionMixin, models.Model):
    """
    Modelo que extiende la información específica para médicos
    """
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='perfil_medico',
        limit_choices_to={'tipo_usuario__in': ['MEDIC']}  # Incluye ambos tipos
    )
    consultorio = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Consultorio o área de trabajo'
    )
    registro_medico = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Número de registro médico'
    )
    especialidades_secundarias = models.ManyToManyField(
        'users.Specialties',
        related_name='medicos_secundarios',
        blank=True
    )

    specialties = models.ForeignKey(Specialties, on_delete=models.PROTECT, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Médico'
        verbose_name_plural = 'Médicos'
        ordering = ['user__last_name', 'user__first_name']

    def __str__(self):
        return f"{self.user.get_full_name()}"
    
@receiver(post_delete, sender=Medico)
def eliminar_imagen_perfil(sender, instance, **kwargs):
    """
    Elimina la imagen asociada cuando se borra un ProfesionalSalud
    """
    if hasattr(instance, 'delete_image'):
        instance.delete_image()