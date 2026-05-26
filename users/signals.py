from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from users.models import CustomUser
from medical.models import Medico
from physiotherapist.models import Fisioterapeuta

@receiver(post_save, sender=CustomUser)
def crear_perfil_profesional(sender, instance, created, **kwargs):
    """
    Crea automáticamente el perfil profesional correspondiente
    """
    if created and instance.tipo_usuario == 'MEDIC':
        Medico.objects.create(user=instance)
    elif created and instance.tipo_usuario == 'FISIO':
        Fisioterapeuta.objects.create(user=instance)