import re
from django import forms
from .models import Fisioterapeuta
from users.models import CustomUser, Specialties
from django.core.exceptions import ValidationError


class FisioterapeutaForm(forms.ModelForm):
    """
    Formulario para crear/editar el perfil de Fisioterapeuta.
    Solo contiene los campos específicos del perfil de fisioterapia.
    El usuario (CustomUser) ya debe existir previamente.
    """
    
    # Campo para buscar y seleccionar el usuario FISIO
    user = forms.ModelChoiceField(
        queryset=CustomUser.objects.filter(tipo_usuario='FISIO'),
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'id_user_select'
        }),
        label='Seleccionar Fisioterapeuta',
        help_text='Busque y seleccione el usuario fisioterapeuta al que desea asignar/editar el perfil'
    )
    
    specialties = forms.ModelChoiceField(
        queryset=Specialties.objects.all(),
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Especialidad principal'
    )
    
    registro_fisioterapia = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Número de registro profesional'
        }),
        label='Número de registro de fisioterapia'
    )
    
    tecnicas_especializadas = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Describa las técnicas en las que está especializado'
        }),
        label='Técnicas especializadas'
    )

    class Meta:
        model = Fisioterapeuta
        fields = [
            'user',
            'registro_fisioterapia',
            'tecnicas_especializadas',
            'specialties'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Si estamos editando un perfil existente
        if self.instance and self.instance.pk:
            # Precargar el usuario
            self.fields['user'].initial = self.instance.user
            # Hacer el campo user de solo lectura en edición (opcional)
            self.fields['user'].disabled = True  # ⬅️ DESHABILITADO EN EDICIÓN
            self.fields['user'].help_text = 'El fisioterapeuta seleccionado no se puede cambiar durante la edición.'
        
        # Aplicar clases Bootstrap a todos los campos, excepto el campo de usuario
        for field_name, field in self.fields.items():
            if field_name != 'user':
                field.widget.attrs.update({'class': 'form-control'})

    def clean_registro_fisioterapia(self):
        registro = self.cleaned_data.get('registro_fisioterapia', '').strip()
        
        # Validar formato: al menos 6 caracteres, solo letras y números
        if not re.match(r'^[A-Za-z0-9]{6,}$', registro):
            raise ValidationError(
                "El número de registro debe tener al menos 6 caracteres y solo contener letras y números."
            )
        
        # Validar unicidad
        qs = Fisioterapeuta.objects.filter(registro_fisioterapia=registro)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError("Ya existe un fisioterapeuta con este número de registro.")
        
        return registro

    def clean_user(self):
        user = self.cleaned_data.get('user')
        
        # Validar que el usuario seleccionado sea FISIO
        if user and user.tipo_usuario != 'FISIO':
            raise ValidationError("El usuario seleccionado debe ser de tipo Fisioterapeuta.")
        
        # Validar que no tenga ya un perfil asignado (solo en creación)
        if not self.instance.pk:
            if Fisioterapeuta.objects.filter(user=user).exists():
                raise ValidationError("Este usuario ya tiene un perfil de fisioterapeuta asignado.")
        
        return user

    def save(self, commit=True):
        fisioterapeuta = super().save(commit=False)
        
        # El usuario ya viene del campo user del formulario
        # No necesitamos tocar CustomUser porque eso se hace en otro formulario
        
        if commit:
            fisioterapeuta.save()
        
        return fisioterapeuta