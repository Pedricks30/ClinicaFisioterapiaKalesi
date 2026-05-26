# expedientes/signals.py
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from paciente.models import Patient
from expedientes.models import Expediente

# Señal para crear expediente automáticamente al crear paciente
@receiver(post_save, sender=Patient)
def crear_expediente_paciente(sender, instance, created, **kwargs):
    """
    Crea automáticamente un expediente cuando se registra un nuevo paciente
    """
    if created:
        # CORREGIDO: Usar nombres y apellidos del paciente para el nombre del expediente
        nombre_completo = f"{instance.nombres} {instance.apellidos}"
        Expediente.objects.create(
            paciente=instance,
            notas_generales=f"Expediente de fisioterapia creado para {nombre_completo}. Pendiente de primera consulta."
        )

@receiver(pre_delete, sender=Patient)
def eliminar_expediente_automatico(sender, instance, **kwargs):
    """
    Elimina automáticamente el expediente al borrar un paciente
    (manejado por CASCADE en el modelo, pero añadido para claridad)
    """
    try:
        instance.expediente.delete()
    except Expediente.DoesNotExist:
        pass