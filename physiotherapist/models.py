from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver
from core.mixins import ImageCompressionMixin, ImageDeletionMixin
from users.models import CustomUser, Specialties

class Fisioterapeuta(ImageCompressionMixin, ImageDeletionMixin, models.Model):
    """
    Modelo que extiende la información específica para fisioterapeutas
    """
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='perfil_fisioterapeuta',
        limit_choices_to={'tipo_usuario': 'FISIO'}
    )
    # Campos específicos para fisioterapeutas
    registro_fisioterapia = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Número de registro de fisioterapia'
    )
    tecnicas_especializadas = models.TextField(
        blank=True,
        verbose_name='Técnicas especializadas'
    )

    specialties = models.ForeignKey(Specialties, on_delete=models.SET_NULL, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Fisioterapeuta'
        verbose_name_plural = 'Fisioterapeutas'
        ordering = ['user__last_name', 'user__first_name']

    def __str__(self):
        return f"Fisioterapeuta: {self.user.get_full_name()}"
    
@receiver(post_delete, sender=Fisioterapeuta)
def eliminar_imagen_perfil(sender, instance, **kwargs):
    """
    Elimina la imagen asociada cuando se borra un Fisioterapeuta
    """
    if hasattr(instance, 'delete_image'):
        instance.delete_image()