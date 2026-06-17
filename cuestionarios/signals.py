# cuestionarios/signals.py
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from .models import RespuestaCuestionario, AnalisisPredictivoEscala, EvolucionPaciente
from .services import AnalisisPredictivoService

@receiver(post_save, sender=RespuestaCuestionario)
def sincronizar_analisis_predictivo(sender, instance, created, **kwargs):
    """Sincroniza automáticamente cuando se guarda una respuesta"""
    if instance.pregunta.tipo_pregunta in ['ESCALA', 'ESCALA_NUMERICA'] and instance.respuesta_escala is not None:
        service = AnalisisPredictivoService()
        service.sincronizar_respuesta_escala(instance)

@receiver(pre_delete, sender=RespuestaCuestionario)
def eliminar_analisis_asociado(sender, instance, **kwargs):
    """Elimina análisis asociado cuando se elimina una respuesta"""
    AnalisisPredictivoEscala.objects.filter(
        consulta_seguimiento=instance.consulta_seguimiento,
        pregunta=instance.pregunta
    ).delete()