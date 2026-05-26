# core/services.py
from datetime import date
from PIL import Image
import os
from io import BytesIO
from django.core.files.base import ContentFile


# =============================================================================
# COMPRESIÓN DE IMÁGENES
# =============================================================================
def compress_image(image_field, quality=70):
    """
    Comprime y convierte una imagen a formato WebP antes de guardarla.

    Args:
        image_field: Campo de imagen de Django (ImageField).
        quality: Calidad de compresión (0-100).

    Returns:
        Nueva imagen procesada en formato WebP.
    """
    try:
        img = Image.open(image_field)

        # Convertir a RGB si la imagen tiene transparencia
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")

        # Redimensionar si es demasiado grande
        max_size = (500, 500)
        img.thumbnail(max_size)

        # Guardar en memoria en formato WebP
        img_io = BytesIO()
        img.save(img_io, format="WEBP", quality=quality)

        return ContentFile(
            img_io.getvalue(),
            name=os.path.splitext(image_field.name)[0] + ".webp"
        )

    except Exception as e:
        print(f"Error al comprimir la imagen: {e}")
        return image_field


# =============================================================================
# CÁLCULO DE EDAD (FUNCIÓN CENTRALIZADA)
# =============================================================================
def calcular_edad(fecha_nacimiento):
    """
    Calcula la edad actual basada en la fecha de nacimiento.
    
    Esta función es genérica y puede ser usada por cualquier modelo
    que tenga un campo de fecha de nacimiento (birthdate, fecha_nacimiento, etc.)

    Args:
        fecha_nacimiento (date): Fecha de nacimiento.

    Returns:
        int or None: Edad en años, o None si la fecha es None.
    """
    if not fecha_nacimiento:
        return None
    
    today = date.today()
    
    # Calcular edad
    edad = today.year - fecha_nacimiento.year
    
    # Ajustar si aún no ha cumplido años este año
    if (today.month, today.day) < (fecha_nacimiento.month, fecha_nacimiento.day):
        edad -= 1
    
    return edad


# =============================================================================
# FUNCIONES ADICIONALES QUE PUEDES AGREGAR A CORE
# =============================================================================

def es_mayor_edad(fecha_nacimiento, edad_minima=18):
    """
    Verifica si una persona es mayor de edad según su fecha de nacimiento.
    
    Args:
        fecha_nacimiento (date): Fecha de nacimiento.
        edad_minima (int): Edad mínima para considerar mayor de edad (default 18).
    
    Returns:
        bool or None: True si es mayor de edad, False si no, None si no hay fecha.
    """
    edad = calcular_edad(fecha_nacimiento)
    if edad is None:
        return None
    return edad >= edad_minima


def formatear_edad(fecha_nacimiento):
    """
    Retorna la edad formateada como string para mostrar en templates.
    
    Args:
        fecha_nacimiento (date): Fecha de nacimiento.
    
    Returns:
        str: Edad formateada (ej: "25 años") o "No disponible".
    """
    edad = calcular_edad(fecha_nacimiento)
    if edad is None:
        return "No disponible"
    return f"{edad} años"


def calcular_edad_exacta(fecha_nacimiento):
    """
    Calcula la edad exacta en años, meses y días.
    
    Args:
        fecha_nacimiento (date): Fecha de nacimiento.
    
    Returns:
        dict or None: Diccionario con años, meses, días o None.
    """
    if not fecha_nacimiento:
        return None
    
    today = date.today()
    
    # Calcular años
    años = today.year - fecha_nacimiento.year
    if (today.month, today.day) < (fecha_nacimiento.month, fecha_nacimiento.day):
        años -= 1
    
    # Calcular meses y días
    if today.month >= fecha_nacimiento.month:
        meses = today.month - fecha_nacimiento.month
    else:
        meses = 12 - fecha_nacimiento.month + today.month
        años -= 1 if años > 0 else 0
    
    if today.day >= fecha_nacimiento.day:
        dias = today.day - fecha_nacimiento.day
    else:
        # Retroceder un mes
        from calendar import monthrange
        dias_mes_anterior = monthrange(today.year, today.month - 1 if today.month > 1 else 12)[1]
        dias = dias_mes_anterior - fecha_nacimiento.day + today.day
        meses -= 1 if meses > 0 else 0
    
    return {
        'años': años,
        'meses': meses,
        'dias': dias,
        'texto': f"{años} años, {meses} meses, {dias} días"
    }


def es_menor_edad(fecha_nacimiento, edad_minima=18):
    """
    Verifica si una persona es menor de edad.
    
    Args:
        fecha_nacimiento (date): Fecha de nacimiento.
        edad_minima (int): Edad mínima para considerar mayor de edad.
    
    Returns:
        bool or None: True si es menor de edad, False si no, None si no hay fecha.
    """
    mayor = es_mayor_edad(fecha_nacimiento, edad_minima)
    if mayor is None:
        return None
    return not mayor


def calcular_proximo_cumpleaños(fecha_nacimiento):
    """
    Calcula cuántos días faltan para el próximo cumpleaños.
    
    Args:
        fecha_nacimiento (date): Fecha de nacimiento.
    
    Returns:
        dict or None: Información del próximo cumpleaños.
    """
    if not fecha_nacimiento:
        return None
    
    today = date.today()
    
    # Cumpleaños este año
    cumple_este_año = date(today.year, fecha_nacimiento.month, fecha_nacimiento.day)
    
    if cumple_este_año < today:
        # Ya pasó, calcular para el próximo año
        cumple_proximo = date(today.year + 1, fecha_nacimiento.month, fecha_nacimiento.day)
    else:
        cumple_proximo = cumple_este_año
    
    dias_faltantes = (cumple_proximo - today).days
    edad_cumplira = calcular_edad(fecha_nacimiento) + (1 if cumple_proximo.year > today.year else 0)
    
    return {
        'fecha': cumple_proximo,
        'dias_faltantes': dias_faltantes,
        'edad_cumplira': edad_cumplira,
        'es_hoy': dias_faltantes == 0
    }