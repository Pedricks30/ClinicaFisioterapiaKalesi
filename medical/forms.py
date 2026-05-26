import re
from django import forms
from django.core.exceptions import ValidationError
from .models import Medico
from users.models import CustomUser, Specialties


class MedicoForm(forms.ModelForm):
    """
    Formulario para crear/editar el perfil de Médico.
    Solo contiene los campos específicos del perfil médico.
    El usuario (CustomUser) ya debe existir previamente.
    """
    
    # Campo para buscar y seleccionar el usuario MEDIC
    user = forms.ModelChoiceField(
        queryset=CustomUser.objects.filter(tipo_usuario='MEDIC'),
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'id_user_select'
        }),
        label='Seleccionar Médico',
        help_text='Busque y seleccione el usuario médico al que desea asignar/editar el perfil'
    )
    
    specialties = forms.ModelChoiceField(
        queryset=Specialties.objects.all(),
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Especialidad principal'
    )
    
    especialidades_secundarias = forms.ModelMultipleChoiceField(
        queryset=Specialties.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={
            'class': 'form-control',
            'id': 'id_especialidades_secundarias'
        }),
        label='Especialidades secundarias',
        help_text='Seleccione una o más especialidades adicionales (opcional)'
    )
    
    consultorio = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej: Consultorio 101, Área de Rehabilitación'
        }),
        label='Consultorio o área de trabajo'
    )
    
    registro_medico = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Número de registro profesional'
        }),
        label='Número de registro médico'
    )

    class Meta:
        model = Medico
        fields = [
            'user',
            'consultorio',
            'registro_medico',
            'especialidades_secundarias',
            'specialties',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Si estamos editando un perfil existente
        if self.instance and self.instance.pk:
            # Precargar el usuario y deshabilitarlo para que no se pueda cambiar
            self.fields['user'].initial = self.instance.user
            self.fields['user'].disabled = True  # ⬅️ DESHABILITADO EN EDICIÓN
            self.fields['user'].help_text = 'El médico seleccionado no se puede cambiar durante la edición.'
        
        # Aplicar clases Bootstrap a todos los campos
        for field_name, field in self.fields.items():
            if 'class' not in field.widget.attrs:
                field.widget.attrs.update({'class': 'form-control'})

    def clean_registro_medico(self):
        registro = self.cleaned_data.get('registro_medico', '').strip()
        
        # Validar formato: al menos 6 caracteres, solo letras y números
        if not re.match(r'^[A-Za-z0-9]{6,}$', registro):
            raise ValidationError(
                "El número de registro médico debe tener al menos 6 caracteres y solo contener letras y números."
            )
        
        # Validar unicidad
        qs = Medico.objects.filter(registro_medico=registro)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError("Ya existe un médico con este número de registro.")
        
        return registro

    def clean_user(self):
        user = self.cleaned_data.get('user')
        
        # Validar que el usuario seleccionado sea MEDIC
        if user and user.tipo_usuario != 'MEDIC':
            raise ValidationError("El usuario seleccionado debe ser de tipo Médico.")
        
        # Validar que no tenga ya un perfil asignado (solo en creación)
        if not self.instance.pk:
            if Medico.objects.filter(user=user).exists():
                raise ValidationError("Este usuario ya tiene un perfil médico asignado.")
        
        return user

    def save(self, commit=True):
        medico = super().save(commit=False)
        
        # El usuario ya viene del campo user del formulario
        # No necesitamos tocar CustomUser porque eso se hace en otro formulario
        
        if commit:
            medico.save()
            # Guardar relaciones ManyToMany (especialidades secundarias)
            self.save_m2m()
        
        return medico