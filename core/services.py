from datetime import date
from PIL import Image
import os
from io import BytesIO
from django.core.files.base import ContentFile

def compress_image(image_field, quality=70):
    """
    Comprime y convierte una imagen a formato WebP antes de guardarla.

    :param image_field: Campo de imagen de Django (ImageField).
    :param quality: Calidad de compresión (0-100).
    :return: Nueva imagen procesada en formato WebP.
    """
    try:
        # Abrir imagen desde el archivo en memoria
        img = Image.open(image_field)

        # Convertir a RGB si la imagen tiene transparencia
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")

        # Redimensionar si es demasiado grande
        max_size = (500, 500)  # Ajustar si se requiere otro tamaño
        img.thumbnail(max_size)

        # Guardar la imagen en memoria en formato WebP
        img_io = BytesIO()
        img.save(img_io, format="WEBP", quality=quality)

        # Crear un nuevo archivo en memoria para el ImageField
        return ContentFile(img_io.getvalue(), name=os.path.splitext(image_field.name)[0] + ".webp")

    except Exception as e:
        print(f"Error al comprimir la imagen: {e}")
        return image_field  # Retornar la imagen original si falla

#Calculador de la edad basandose en fecha actual y fecha de nacimiento
def calcular_edad(self):
        """
        Calcular edad actual basado en fecha de nacimiento
        :return: int edad
        """
        if self.birthdate:
            # Obtener fecha de hoy
            today = date.today()
            # Calcular Edad
            age = today.year - self.birthdate.year - (
                    (today.month, today.day) < (self.birthdate.month, self.birthdate.day))
            return age

        # Si no tiene fecha su edad es 0
        return 0
