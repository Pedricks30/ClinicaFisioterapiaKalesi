# core/templatetags/core_tags.py
from django import template
from core.services import calcular_edad, formatear_edad, es_mayor_edad, es_menor_edad

register = template.Library()


@register.filter(name='calcular_edad')
def edad_filter(fecha_nacimiento):
    """
    Filtro de template para calcular la edad.
    
    Uso en template:
        {{ user.birthdate|calcular_edad }}
        {{ paciente.fecha_nacimiento|calcular_edad }}
    """
    return calcular_edad(fecha_nacimiento)


@register.filter(name='edad_formateada')
def edad_formateada_filter(fecha_nacimiento):
    """
    Filtro que retorna la edad formateada como "25 años".
    
    Uso en template:
        {{ user.birthdate|edad_formateada }}
    """
    return formatear_edad(fecha_nacimiento)


@register.filter(name='es_mayor')
def es_mayor_filter(fecha_nacimiento, edad_minima=18):
    """
    Filtro para verificar si es mayor de edad.
    
    Uso en template:
        {{ paciente.fecha_nacimiento|es_mayor }}
        {{ paciente.fecha_nacimiento|es_mayor:21 }}
    """
    return es_mayor_edad(fecha_nacimiento, edad_minima)


@register.filter(name='es_menor')
def es_menor_filter(fecha_nacimiento, edad_minima=18):
    """
    Filtro para verificar si es menor de edad.
    
    Uso en template:
        {{ paciente.fecha_nacimiento|es_menor }}
    """
    return es_menor_edad(fecha_nacimiento, edad_minima)


@register.simple_tag
def edad_tag(fecha_nacimiento):
    """
    Tag para calcular y mostrar la edad.
    
    Uso en template:
        {% edad_tag user.birthdate %}
    """
    edad = calcular_edad(fecha_nacimiento)
    if edad is None:
        return "No disponible"
    return f"{edad} años"