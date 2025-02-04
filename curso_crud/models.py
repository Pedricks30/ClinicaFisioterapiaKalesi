from django.contrib.auth.models import AbstractUser
from django.db import models
from PIL import Image
import os

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
    document_number = models.CharField(max_length=40)  # Número de documento
    profile_image = models.ImageField(upload_to='profile_images/', null=True, blank=True)

    # Relaciones con otras tablas
    document_type = models.ForeignKey(DocumentType, on_delete=models.SET_NULL, null=True, blank=True)
    access_level = models.ForeignKey(AccessLevel, on_delete=models.SET_NULL, null=True, blank=True)

    def save(self, *args, **kwargs):
        # Guardar el objeto primero para obtener la ruta de la imagen
        super().save(*args, **kwargs)

        # Comprimir y convertir la imagen si se ha subido una
        if self.profile_image:
            try:
                # Verificar si el archivo es una imagen
                if self.profile_image.name.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                    compressed_image_path = compress_image(self.profile_image)
                    self.profile_image.name = os.path.relpath(compressed_image_path, start=os.path.dirname(self.profile_image.path))
                    super().save(*args, **kwargs)  # Guardar de nuevo con la nueva imagen
            except Exception as e:
                print(f"Error al comprimir la imagen: {e}")

    def __str__(self):
        return self.username

def compress_image(image, quality=70):
    """
    Comprime una imagen y la convierte a WebP.
    :param image: La imagen a comprimir.
    :param quality: Calidad de compresión (0-100).
    :return: La ruta de la imagen comprimida.
    """
    try:
        img = Image.open(image)
        output_path = os.path.splitext(image.path)[0] + '.webp'  # Cambia la extensión a .webp
        img.save(output_path, 'WEBP', quality=quality)
        return output_path
    except Exception as e:
        print(f"Error al procesar la imagen: {e}")
        return image.path  # Devuelve la ruta original si hay un error