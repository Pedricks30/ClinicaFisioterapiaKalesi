from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model

# Option 1: Use settings.AUTH_USER_MODEL for foreign keys (recommended for models.py)
# Option 2: Use get_user_model() for other cases (like in methods)

class Patient(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='paciente')
    fecha_nacimiento = models.DateField(null=True, blank=True)
    genero = models.CharField(max_length=10, choices=[
        ('M', 'Masculino'), 
        ('F', 'Femenino'),
        ('O', 'Otro')
    ], null=True, blank=True)
    telefono = models.CharField(max_length=15, null=True, blank=True)
    direccion = models.TextField(null=True, blank=True)
    alergias = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        User = get_user_model()
        return f"{self.user.get_full_name() or self.user.username}"

class MedicalUser(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    # ... (your existing fields for MedicalUser)