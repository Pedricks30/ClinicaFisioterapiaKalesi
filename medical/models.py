from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver
from core.mixins import ImageCompressionMixin, ImageDeletionMixin
from users.models import DocumentType, Specialties

class MedicalUser(ImageCompressionMixin, ImageDeletionMixin, models.Model):
    # Image field
    profile_image = models.ImageField(upload_to='profile_images/', default='profile_images_default/user_default.webp')
    # Personal information
    name = models.CharField(max_length=255)
    SEXO_CHOICES = [
        ('Masculino', 'Masculino'),
        ('Femenino', 'Femenino'),
        ('Otro', 'Otro')
    ]
    sexo = models.CharField(max_length=20, choices=SEXO_CHOICES)
    email = models.EmailField(unique=True)
    
    # Address information
    address1 = models.CharField(max_length=255, null=True, blank=True)  # Dirección 1
    
    phone_number = models.CharField(max_length=20, null=True, blank=True)  # Número de teléfono completo
    document_number = models.CharField(max_length=40, unique=True)  # Asegura que el Número de documento
    
    # Nationality information
    country = models.CharField(max_length=100, null=True, blank=True)  # País
    birthdate = models.DateField(null=True, blank=True)  # Fecha de nacimiento
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Relaciones con otras tablas
    document_type = models.ForeignKey(DocumentType, on_delete=models.SET_NULL, null=True, blank=True)
    specialties = models.ForeignKey(Specialties, on_delete=models.SET_NULL, null=True, blank=True)
    

    def __str__(self):
        return str(self.name) if self.name is not None else ""
    
    class Meta:
        verbose_name = 'Profesional Médico'
        verbose_name_plural = 'Profesionales Médicos'

@receiver(post_delete)
def delete_image_on_post_delete(sender, instance, **kwargs):
    """
    Elimina la imagen asociada a un objeto cuando se elimina el objeto.
    """
    if hasattr(instance, 'delete_image'):
        instance.delete_image()