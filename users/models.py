from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver
from core.mixins import ImageCompressionMixin, ImageDeletionMixin

# Modelo para Tipo de Documento
class DocumentType(models.Model):
    id_document = models.AutoField(primary_key=True)
    document_type = models.CharField(max_length=50, unique=True)
    document_description = models.CharField(max_length=255, unique=True)  # Descripción del tipo de documento
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.document_type
    
# Modelo para Nivel de Acceso (Roles)
class AccessLevel(models.Model):
    id_access_level = models.AutoField(primary_key=True)
    access_level = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.access_level
    
# Modelo para Especialidades de medicos
class Specialties(models.Model):
    id_specialty = models.AutoField(primary_key=True)
    specialties = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.specialties

# Modelo de Usuario Personalizado
class CustomUser(AbstractUser, ImageCompressionMixin, ImageDeletionMixin):
    # Campos adicionales
    email = models.EmailField(unique=True) 
    age = models.IntegerField(null=True, blank=True)  # Edad
    phone_number = models.CharField(max_length=20, null=True, blank=True)  # Número de teléfono completo
    address1 = models.CharField(max_length=255, null=True, blank=True)  # Dirección 1
    address2 = models.CharField(max_length=255, null=True, blank=True)  # Dirección 2
    country = models.CharField(max_length=100, null=True, blank=True)  # País
    birthdate = models.DateField(null=True, blank=True)  # Fecha de nacimiento
    document_number = models.CharField(max_length=40, unique=True)  # Asegura que el Número de documento
    profile_image = models.ImageField(upload_to='profile_images/', default='profile_images_default/user_default.webp')
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    # Relaciones con otras tablas
    document_type = models.ForeignKey(DocumentType, on_delete=models.SET_NULL, null=True, blank=True)
    access_level = models.ForeignKey(AccessLevel, on_delete=models.SET_NULL, null=True, blank=True)
    specialties = models.ForeignKey(Specialties, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.username

@receiver(post_delete)
def delete_image_on_post_delete(sender, instance, **kwargs):
    """
    Elimina la imagen asociada a un objeto cuando se elimina el objeto.
    """
    if hasattr(instance, 'delete_image'):
        instance.delete_image()