from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_delete
from core.mixins import ImageCompressionMixin, ImageDeletionMixin
from users.models import DocumentType, Specialties

# Create your models here.
# Modelo para Especialidades de medicos
class Staff(ImageCompressionMixin, ImageDeletionMixin, models.Model):
    id_staff = models.AutoField(primary_key=True)
    email = models.EmailField(unique=True) 
    name = models.CharField(max_length=50, null=True, blank=True)  # Nombre
    phone_number = models.CharField(max_length=20, null=True, blank=True)  # Número de teléfono completo
    address1 = models.CharField(max_length=255, null=True, blank=True)  # Dirección 1
    document_number = models.CharField(max_length=40, unique=True)  # Asegura que el Número de documento
    sex = models.CharField(max_length=10, null=True, blank=True)  # Sexo
    birthdate = models.DateField(null=True, blank=True)  # Fecha de nacimiento
    profile_image = models.ImageField(upload_to='profile_images/', default='profile_images_default/user_default.webp')
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    # Relaciones con otras tablas
    document_type = models.ForeignKey(DocumentType, on_delete=models.SET_NULL, null=True, blank=True)
    specialties = models.ForeignKey(Specialties, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.email
    
@receiver(post_delete)
def delete_image_on_post_delete(sender, instance, **kwargs):
    """
    Elimina la imagen asociada a un objeto cuando se elimina el objeto.
    """
    if hasattr(instance, 'delete_image'):
        instance.delete_image()
