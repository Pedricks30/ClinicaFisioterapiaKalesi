import re
from django.utils import timezone
from django import forms
from django.core.exceptions import ValidationError
from paciente.models import Patient
from users.models import CustomUser, DocumentType

class PatientForm(forms.ModelForm):
    # Campos personalizados con widgets específicos
    nombres = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label='Nombres',
        help_text='Ingrese los nombres del paciente (máximo 100 caracteres).'
    )

    apellidos = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label='Apellidos',

    )
    tipo_documento = forms.ModelChoiceField(
        queryset=DocumentType.objects.all(),
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Tipo de Documento',
        help_text='Seleccione el tipo de documento del paciente.'
    )
    documento_identidad = forms.CharField(
        max_length=40,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label='Número de Documento'
    )
    nacionalidad = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'country'}),
        label='Nacionalidad'
    )
    sexo = forms.ChoiceField(
        choices=Patient.SEXO_CHOICES,
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Sexo'
    )
    fecha_nacimiento = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'placeholder': 'DD/MM/AAAA'},
        format='%Y-%m-%d'),  # Formato interno que usa el input date
        label='Fecha de Nacimiento',
        input_formats=['%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y']  # Formatos aceptados
    )
    foto_perfil = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control'}),
        label='Imagen de Perfil'
    )
    estado_civil = forms.ChoiceField(
        choices=Patient.ESTADO_CIVIL_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Estado Civil'
    )
    ocupacion = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label='Ocupación',
        help_text='Ingrese la ocupación del paciente (máximo 100 caracteres).'
    )
    lugar_nacimiento = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label='Lugar de Nacimiento',
    )
    estado = forms.ChoiceField(
        choices=[(True, 'Activo'), (False, 'Inactivo')],
        required=True,
        initial=True,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Estado',
        help_text="Indica si el paciente está activo. Desmarque esta opción en lugar de eliminar el registro."
    )
    numero_telefono = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'phone'}),
        label='Celular'
    )
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
        label='Correo Electrónico'
    )
    direccion = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        label='Dirección'
    )
    nombre_acompanante = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label='Nombre del Acompañante',
        help_text='Ingrese el nombre del acompañante o responsable del paciente'
    )
    parentesco_acompanante = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label='Parentesco',
        help_text='Ingrese el parentesco del acompañante con el paciente (ej. padre, madre, amigo, etc.).'
    )
    telefono_acompanante = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'phone'}),
        label='Teléfono del Acompañante',
    )
    direccion_acompanante = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        label='Dirección del Acompañante',
        help_text='Ingrese la dirección del acompañante o responsable del paciente.'
    )
    creado_por = forms.ModelChoiceField(
        queryset=CustomUser.objects.filter(tipo_usuario__in=['RECEP', 'ADMIN', 'MEDIC']),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Creado por',
        disabled=True
    )

    class Meta:
        model = Patient
        fields = [
            'nombres', 'apellidos', 'tipo_documento', 'documento_identidad',
            'nacionalidad', 'sexo', 'fecha_nacimiento', 'foto_perfil',
            'estado_civil', 'ocupacion', 'lugar_nacimiento', 'estado',
            'numero_telefono', 'email', 'direccion',
            'nombre_acompanante', 'parentesco_acompanante', 
            'telefono_acompanante', 'direccion_acompanante','creado_por'
        ]

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Configuración adicional de campos
        self.fields['fecha_nacimiento'].widget.attrs['max'] = timezone.now().date()
        
        # Si estamos editando, configuramos el creado_por
        if self.instance and self.instance.pk:
            self.fields['creado_por'].initial = self.instance.creado_por
            self.fields['creado_por'].disabled = True
        
        # Asignar el usuario que crea el registro
        if user:
            self.user = user
    
    def clean(self):
        cleaned_data = super().clean()

        # 1. Validación para pacientes menores de edad requieren acompañante
        fecha_nacimiento = cleaned_data.get('fecha_nacimiento')
        nombre_acompanante = cleaned_data.get('nombre_acompanante')
        parentesco_acompanante = cleaned_data.get('parentesco_acompanante')
        telefono_acompanante = cleaned_data.get('telefono_acompanante')

        if fecha_nacimiento:
            hoy = timezone.now().date()
            edad = hoy.year - fecha_nacimiento.year - ((hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day))

            if edad < 18:  # Si es menor de edad
                # Los campos del acompañante son OBLIGATORIOS para menores
                if not nombre_acompanante:
                    self.add_error('nombre_acompanante', "Para pacientes menores de edad se requiere un acompañante")
                if not parentesco_acompanante:
                    self.add_error('parentesco_acompanante', "Debe especificar el parentesco del acompañante")
                if not telefono_acompanante:
                    self.add_error('telefono_acompanante', "Debe proporcionar un teléfono de contacto del acompañante")
                if not telefono_acompanante:
                    self.add_error('telefono_acompanante', "Debe proporcionar un teléfono de contacto del acompañante/responsable")

        # 2. Validación de email y teléfono no pueden ser iguales al acompañante
        email = cleaned_data.get('email')
        telefono = cleaned_data.get('numero_telefono')

        if email and email == cleaned_data.get('email_acompanante', ''):
            self.add_error('email', "El email no puede ser el mismo que el del acompañante")

        if telefono and telefono == telefono_acompanante:
            self.add_error('numero_telefono', "El teléfono no puede ser el mismo que el del acompañante")

        return cleaned_data

    def clean_documento_identidad(self):
        documento = self.cleaned_data.get('documento_identidad')
        if not documento:
            return documento
            
        # Validar formato (ejemplo: solo números para algunos tipos de documento)
        if not re.match(r'^[0-9]+$', documento):
            raise ValidationError("El número de documento solo debe contener dígitos.")
            
        # Validar unicidad
        qs = Patient.objects.filter(documento_identidad=documento)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError("Ya existe un paciente con este número de documento.")
        return documento

    def clean_fecha_nacimiento(self):
        fecha = self.cleaned_data.get('fecha_nacimiento')
        if fecha and fecha > timezone.now().date():
            raise ValidationError("La fecha de nacimiento no puede ser futura.")
        return fecha

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            return email
            
        # Verificar si el email ya está en uso por otro paciente
        qs = Patient.objects.filter(email=email)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError("Este correo electrónico ya está registrado.")
        return email

    def save(self, commit=True):
        paciente = super().save(commit=False)
        
        # Asignar el usuario que creó/modificó el registro
        if hasattr(self, 'user'):
            paciente.creado_por = self.user
            
        if commit:
            paciente.save()
            
        return paciente