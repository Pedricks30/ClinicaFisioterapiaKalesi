# expedientes/templatetags/form_filters.py
from django import template

register = template.Library()

@register.filter
def split(value, arg):
    """Divide una cadena por el separador dado"""
    return value.split(arg)