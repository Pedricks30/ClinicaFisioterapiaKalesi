# cuestionarios/admin.py
from django.contrib import admin
from .models import (
    Cuestionario, PreguntaCuestionario, RespuestaCuestionario,
    AnalisisPredictivoEscala, EvolucionPaciente
)

@admin.register(Cuestionario)
class CuestionarioAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'tipo_cuestionario', 'activo', 'created_at']
    list_filter = ['tipo_cuestionario', 'activo']
    search_fields = ['nombre', 'descripcion']

@admin.register(PreguntaCuestionario)
class PreguntaCuestionarioAdmin(admin.ModelAdmin):
    list_display = ['texto_pregunta', 'cuestionario', 'tipo_pregunta', 'orden', 'es_indicador_clave']
    list_filter = ['tipo_pregunta', 'cuestionario', 'es_indicador_clave']
    search_fields = ['texto_pregunta']

@admin.register(RespuestaCuestionario)
class RespuestaCuestionarioAdmin(admin.ModelAdmin):
    list_display = ['consulta_seguimiento', 'pregunta', 'fecha_respuesta']
    list_filter = ['fecha_respuesta', 'pregunta__tipo_pregunta']
    readonly_fields = ['fecha_respuesta']

@admin.register(AnalisisPredictivoEscala)
class AnalisisPredictivoEscalaAdmin(admin.ModelAdmin):
    list_display = ['consulta_seguimiento', 'pregunta', 'valor_escala', 'tendencia', 'prediccion_siguiente']
    list_filter = ['tendencia', 'supera_umbral_alarma', 'es_linea_base']
    readonly_fields = ['valor_normalizado', 'created_at', 'updated_at']

@admin.register(EvolucionPaciente)
class EvolucionPacienteAdmin(admin.ModelAdmin):
    list_display = ['expediente', 'tipo_evaluacion', 'porcentaje_mejoria', 'tendencia_general']
    list_filter = ['tendencia_general']
    readonly_fields = ['ultima_actualizacion']