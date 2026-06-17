from django.db import models
from core.services import compress_image

class ImageCompressionMixin(models.Model):
    """
    Mixin que agrega funcionalidad de compresión de imágenes antes de guardarlas.
    """
    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        # Verificar si hay una nueva imagen para comprimir
        if (hasattr(self, 'profile_image') and 
            self.profile_image and 
            not getattr(self, '_compressing', False) and
            self._is_new_image()):  # Solo comprimir si es una imagen nueva
            self._compressing = True
            try:
                self.profile_image = compress_image(self.profile_image)
            except Exception as e:
                print(f"Error compressing image: {e}")
            finally:
                self._compressing = False
        super().save(*args, **kwargs)
    
    def _is_new_image(self):
        """Verifica si la imagen es nueva o ya existía"""
        if not self.pk:
            return True  # Es un nuevo registro
        try:
            old_instance = self.__class__.objects.get(pk=self.pk)
            # Comparar si la imagen ha cambiado
            if hasattr(old_instance, 'profile_image'):
                old_image = old_instance.profile_image
                new_image = self.profile_image
                return old_image != new_image
            return True
        except self.__class__.DoesNotExist:
            return True

class ImageDeletionMixin:
    """Mixin reutilizable para eliminar imágenes asociadas a modelos cuando se borran."""
    
    def delete_image(self):
        """ Elimina la imagen del sistema de archivos si existe. """
        if hasattr(self, 'profile_image') and self.profile_image:
            try:
                storage = self.profile_image.storage
                path = self.profile_image.path
                if storage.exists(path):
                    storage.delete(path)
                    print(f"Imagen eliminada: {path}")
            except Exception as e:
                print(f"Error al eliminar la imagen: {e}")

    def delete(self, *args, **kwargs):
        """ Sobreescribe delete() para eliminar la imagen antes de borrar el objeto. """
        self.delete_image()
        super().delete(*args, **kwargs)