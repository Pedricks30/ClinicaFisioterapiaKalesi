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

    specialties = models.ForeignKey(Specialties, on_delete=models.SET_NULL, null=True, blank=True)

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





#DEBO QUITAR ESTAS DOS TABLAS DE ESTE MODELO Y CREAR UN NUEVO MODELO PARA LOS CONSULTORIOS, 
# ASIGNACIONES, ETC. PARA QUE NO SE ME LLENE DE COSAS QUE NO SON DE LOS MÉDICOS. SI NO, ME VA A QUEDAR 
# UN MODELO MUY GRANDE Y DESORDENADO.
class Consultorio(models.Model):
    """
    Modelo para gestionar los consultorios médicos
    """
    nombre = models.CharField(max_length=100, unique=True)
    ubicacion = models.CharField(max_length=255)
    piso = models.CharField(max_length=10, blank=True)
    numero = models.CharField(max_length=10)
    activo = models.BooleanField(default=True)
    equipo_especial = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Consultorio'
        verbose_name_plural = 'Consultorios'
        ordering = ['nombre']

    def __str__(self):
        return f"Consultorio {self.nombre} - Piso {self.piso}"


class AsignacionConsultorio(models.Model):
    """
    Asignación de consultorios a profesionales
    """
    profesional = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='asignaciones_consultorio',
        limit_choices_to={'tipo_usuario__in': ['MEDIC', 'FISIO']}
    )
    consultorio = models.ForeignKey(
        Consultorio,
        on_delete=models.CASCADE,
        related_name='asignaciones_profesional'
    )
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField(null=True, blank=True)
    activo = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Asignación de Consultorio'
        verbose_name_plural = 'Asignaciones de Consultorios'
        ordering = ['-fecha_inicio']
        constraints = [
            models.UniqueConstraint(
                fields=['profesional', 'consultorio', 'activo'],
                name='unique_active_assignment'
            )
        ]

    def __str__(self):
        return f"{self.profesional} - {self.consultorio}"