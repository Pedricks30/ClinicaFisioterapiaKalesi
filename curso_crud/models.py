from django.contrib.auth.models import AbstractUser
from django.db import models

# Modelo para Tipo de Documento
class DocumentType(models.Model):
    id_document = models.AutoField(primary_key=True)
    document_type = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.document_type

# Modelo para Nivel de Acceso (Roles)
class AccessLevel(models.Model):
    id_access_level = models.AutoField(primary_key=True)
    access_level = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.access_level

# Modelo de Usuario Personalizado
class CustomUser(AbstractUser):
    # Campos adicionales
    age = models.IntegerField(null=True, blank=True)  # Edad
    telephone_prefix = models.CharField(max_length=5, null=True, blank=True)  # Prefijo de teléfono
    phone = models.CharField(max_length=20, null=True, blank=True)  # Teléfono
    address1 = models.CharField(max_length=255, null=True, blank=True)  # Dirección 1
    address2 = models.CharField(max_length=255, null=True, blank=True)  # Dirección 2
    country = models.CharField(max_length=100, null=True, blank=True)  # País
    birthdate = models.DateField(null=True, blank=True)  # Fecha de nacimiento
    document_number = models.CharField(max_length=40) # Numero de documento

    # Relaciones con otras tablas
    document_type = models.ForeignKey(DocumentType, on_delete=models.SET_NULL, null=True, blank=True)
    access_level = models.ForeignKey(AccessLevel, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.username