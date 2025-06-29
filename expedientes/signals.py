from django.db.models.signals import post_save
from django.dispatch import receiver
from paciente.models import Patient
from expedientes.models import Expediente

@receiver(post_save, sender=Patient)
def crear_expediente(sender, instance, created, **kwargs):
    if created:
        Expediente.objects.create(paciente=instance)