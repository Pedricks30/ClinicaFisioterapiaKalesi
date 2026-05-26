from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver
from core.mixins import ImageCompressionMixin, ImageDeletionMixin

# Modelo para Tipo de Documento
class DocumentType(models.Model):
    id_document = models.AutoField(primary_key=True)
    document_type = models.CharField(max_length=50, unique=True)
    document_description = models.CharField(max_length=255, unique=True)  # Descripción del tipo de documento
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.document_type
# Modelo para Especialidades de medicos
class Specialties(models.Model):
    id_specialty = models.AutoField(primary_key=True)
    specialties = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.specialties

# Modelo de Usuario Personalizado
class CustomUser(AbstractUser, ImageCompressionMixin, ImageDeletionMixin):
    # Campos adicionales
    # Tipos de usuario
    TIPO_USUARIO_CHOICES = [
        ('ADMIN', 'Administrador'),
        ('RECEP', 'Recepcionista'),
        ('MEDIC', 'Médico'),
        ('FISIO', 'Fisioterapeuta'),
    ]
    SEXO_CHOICES = [
        ('Masculino', 'Masculino'),
        ('Femenino', 'Femenino'),
        ('Otro', 'Otro'),
    ]
    
    # Campos base
    tipo_usuario = models.CharField(max_length=5, choices=TIPO_USUARIO_CHOICES)
    email = models.EmailField(unique=True)
    sexo = models.CharField(max_length=10, choices=SEXO_CHOICES, null=True, blank=True)  # Sexo
    phone_number = models.CharField(max_length=20, null=True, blank=True)  # Número de teléfono completo
    address1 = models.CharField(max_length=255, null=True, blank=True)  # Dirección 1
    address2 = models.CharField(max_length=255, null=True, blank=True)  # Dirección 2
    country = models.CharField(max_length=30, null=True, blank=True)  # País
    birthdate = models.DateField(null=True, blank=True)  # Fecha de nacimiento
    document_number = models.CharField(max_length=40, unique=True)  # Asegura que el Número de documento
    profile_image = models.ImageField(upload_to='profile_images/', default='profile_images_default/user_default.webp')
    # Relaciones con otras tablas
    document_type = models.ForeignKey(DocumentType, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_tipo_usuario_display()})"

    @property
    def is_medico(self):
        return self.tipo_usuario == 'MEDIC'
    
    @property
    def is_fisio(self):  # Cambiado de is_fisioterapeuta a is_fisio para coincidir con tu tipo_usuario
        return self.tipo_usuario == 'FISIO'
    
    @property
    def is_recepcionista(self):
        return self.tipo_usuario == 'RECEP'

    @property
    def registro_profesional(self):
        if hasattr(self, 'perfil_medico'):
            return self.perfil_medico.registro_profesional
        return None
    
    @property
    def horarios_activos(self):
        if self.is_medico:
            return self.horarios.filter(activo=True)
        return None
    
    '''Así puedes acceder a la especialidad desde cualquier vista con user.perfil_profesional.specialties.'''
    # users/models.py

    @property
    def perfil_profesional(self):
        """
        Retorna el perfil extendido del profesional (Médico o Fisioterapeuta)
        según corresponda su tipo de usuario.
        """
        if self.is_medico and hasattr(self, 'perfil_medico'):
            return self.perfil_medico
        elif self.is_fisio and hasattr(self, 'perfil_fisioterapeuta'):
            return self.perfil_fisioterapeuta # Retorna el objeto completo, igual que arriba
        return None

@receiver(post_delete)
def delete_image_on_post_delete(sender, instance, **kwargs):
    """
    Elimina la imagen asociada a un objeto cuando se elimina el objeto.
    """
    if hasattr(instance, 'delete_image'):
        instance.delete_image()
