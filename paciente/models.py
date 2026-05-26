from django.utils import timezone
from django.db import models
from core.services import calcular_edad, es_menor_edad
from users.models import CustomUser, DocumentType
from django.db.models.signals import post_delete
from django.dispatch import receiver
from core.mixins import ImageCompressionMixin, ImageDeletionMixin
from core.services import compress_image


class Patient(ImageCompressionMixin, ImageDeletionMixin, models.Model):
    ESTADO_CIVIL_CHOICES = [
        ('SOLTERO', 'Soltero/a'),
        ('CASADO', 'Casado/a'),
        ('DIVORCIADO', 'Divorciado/a'),
        ('VIUDO', 'Viudo/a'),
        ('UNION_LIBRE', 'Unión libre'),
    ]
    
    SEXO_CHOICES = [
        ('Masculino', 'Masculino'),
        ('Femenino', 'Femenino'),
        ('Otro', 'Otro'),
    ]
    TIPO_SANGRE_CHOICES = [
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-'),
    ]
    
    # Relación con el usuario del sistema (si tiene)
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='paciente_profile'
    )
    
    # Datos personales
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    tipo_documento = models.ForeignKey(
        DocumentType, 
        on_delete=models.PROTECT,
        verbose_name="Tipo de documento"
    )
    documento_identidad = models.CharField(
        max_length=40,
        unique=True,
        verbose_name="Número de documento"
    )
    nacionalidad = models.CharField(max_length=30, null=True, blank=True)
    sexo = models.CharField(max_length=10, choices=SEXO_CHOICES)
    fecha_nacimiento = models.DateField()
    foto_perfil = models.ImageField(upload_to='profile_images/', default='profile_images_default/user_default.webp')
    estado_civil = models.CharField(
        max_length=20,
        choices=ESTADO_CIVIL_CHOICES,
        blank=True
    )
    ocupacion = models.CharField(max_length=100, blank=True)
    lugar_nacimiento = models.CharField(max_length=100, blank=True)
    estado = models.BooleanField(default=True)
    
    # Datos de contacto
    numero_telefono = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    direccion = models.TextField()
    
    # Datos médicos importantes
    tipo_sangre = models.CharField(
        max_length=3,
        choices=TIPO_SANGRE_CHOICES,
        blank=True
    )
    alergias = models.TextField(blank=True)
    condiciones_medicas = models.TextField(blank=True)
    
    # Datos del acompañante/responsable
    nombre_acompanante = models.CharField(max_length=200, blank=True)
    parentesco_acompanante = models.CharField(max_length=50, blank=True)
    telefono_acompanante = models.CharField(max_length=20, blank=True)
    direccion_acompanante = models.TextField(blank=True)
    
    # Metadata
    creado_por = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name='pacientes_creados',
        limit_choices_to={'tipo_usuario__in': ['RECEP', 'ADMIN', 'MEDIC']}
    )
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Paciente'
        verbose_name_plural = 'Pacientes'
        ordering = ['apellidos', 'nombres']
        indexes = [
            models.Index(fields=['apellidos', 'nombres']),
            models.Index(fields=['documento_identidad']),
        ]

    def __str__(self):
        return f"{self.apellidos}, {self.nombres} ({self.documento_identidad})"

    @property
    def edad(self):
        """Calcula la edad del paciente"""
        return calcular_edad(self.fecha_nacimiento)
    
    @property
    def es_menor(self):
        """Verifica si el paciente es menor de edad"""
        return es_menor_edad(self.fecha_nacimiento)
    
    @property
    def es_mayor(self):
        """Verifica si el paciente es mayor de edad"""
        from core.services import es_mayor_edad
        return es_mayor_edad(self.fecha_nacimiento)
    
    @property
    def contacto_emergencia(self):
        """Obtiene el contacto de emergencia (acompañante o responsable)"""
        if self.nombre_acompanante:
            return {
                'nombre': self.nombre_acompanante,
                'parentesco': self.parentesco_acompanante,
                'telefono': self.telefono_acompanante,
                'direccion': self.direccion_acompanante
            }
        return None
    
    def save(self, *args, **kwargs):
        # Si es un nuevo paciente y no tiene foto, asignar la imagen por defecto
        if not self.pk and not self.foto_perfil:
            # La imagen por defecto ya está configurada en el campo
            pass
        
        # Comprimir imagen si es necesario
        if self.foto_perfil and hasattr(self.foto_perfil, 'file'):
            try:
                compressed = compress_image(self.foto_perfil)
                if compressed:
                    self.foto_perfil = compressed
            except Exception as e:
                print(f"Error compressing image: {e}")
        
        super().save(*args, **kwargs)

@receiver(post_delete, sender=Patient)
def eliminar_imagen_perfil(sender, instance, **kwargs):
    """
    Elimina la imagen asociada cuando se borra un Paciente
    """
    if hasattr(instance, 'delete_image'):
        instance.delete_image()