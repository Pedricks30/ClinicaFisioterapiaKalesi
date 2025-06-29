from django.db import models
from core.services import compress_image

class ImageCompressionMixin(models.Model):
    """
    Mixin que agrega funcionalidad de compresión de imágenes antes de guardarlas.
    """
    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if hasattr(self, 'profile_image') and self.profile_image and not getattr(self, '_compressing', False):
            self._compressing = True
            self.profile_image = compress_image(self.profile_image)
        super().save(*args, **kwargs)

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
            except Exception as e:
                print(f"Error al eliminar la imagen: {e}")

    def delete(self, *args, **kwargs):
        """ Sobreescribe delete() para eliminar la imagen antes de borrar el objeto. """
        self.delete_image()
        super().delete(*args, **kwargs)