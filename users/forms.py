from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from .models import CustomUser, DocumentType, AccessLevel, Specialties
from django.core.exceptions import ValidationError

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
        label="Correo electrónico"
    )
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label='Nombres',
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label='Apellidos'
    )
    age = forms.IntegerField(
        required=True,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        label='Edad'
    )
    phone_number = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'phone'}),
        label='Celular'
    )
    address1 = forms.CharField(
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label='Dirección 1'
    )
    address2 = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label='Dirección 2'
    )
    country = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'country'}),
        label='País'
    )
    birthdate = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        label='Fecha de Nacimiento'
    )
    document_type = forms.ModelChoiceField(
        queryset=DocumentType.objects.all(),
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Tipo de Documento'
    )
    document_number = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label='Número de documento'
    )
    access_level = forms.ModelChoiceField(
        queryset=AccessLevel.objects.all(),
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Nivel de Acceso'
    )
    is_active = forms.ChoiceField(
        choices=[(True, 'Activo'), (False, 'Inactivo')],
        required=True,
        initial=True,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Estado de Usuario',
        help_text="Indica si el usuario debe ser tratado como activo. Desmarque esta opción en lugar de borrar la cuenta."
    )
    is_staff = forms.ChoiceField(
        choices=[(True, 'Permitido'), (False, 'Denegado')],
        required=True,
        initial=True,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Es staff',
        help_text="Indica si el usuario puede entrar en este sitio de administración."
    )
    is_superuser = forms.ChoiceField(
        choices=[(True, 'Permitido'), (False, 'Denegado')],
        required=True,
        initial=True,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Estado de superusuario',
        help_text="Indica que este usuario tiene todos los permisos sin asignárselos explícitamente."
    )
    specialties = forms.ModelChoiceField(
        queryset=Specialties.objects.all(),
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Especialidad'
    )

    class Meta:
        model = CustomUser
        fields = (
            'username', 'email', 'first_name', 'last_name', 'age', 'phone_number',
            'address1', 'address2', 'country', 'birthdate', 'document_type', 'document_number',
            'access_level', 'password1', 'password2', 'is_active', 'is_staff', 'is_superuser', 'specialties'
        )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Aplicar clases de Bootstrap a todos los campos
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})

    def clean_username(self):
        username = self.cleaned_data['username']
        if self.instance and self.instance.username == username:
            return username
        if CustomUser.objects.filter(username=username).exists():
            raise forms.ValidationError("Ya existe un usuario con este nombre.")
        return username

class DocumentTypeForm(forms.ModelForm):
    document_type = forms.CharField(
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej: DNI, Pasaporte, Carné de Extranjería'
        }),
        label='Tipo de Documento',
        help_text='Ingrese un nombre único para el tipo de documento'
    )
    document_description = forms.CharField(
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Decripción del tipo de documento'
        }),
        label='Descripción Tipo de Documento',
        help_text='Ingrese una descripción única para el tipo de documento'
    )
    
    class Meta:
        model = DocumentType
        fields = ['document_type', 'document_description']
        error_messages = {
            'document_type': {
                'unique': "Este tipo de documento ya existe.",
            },
            'document_description': {
                'unique': "Esta descripción de tipo de documento ya existe.",
            }
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.error_messages = {
                'required': f'El campo {field.label} es obligatorio',
            }

    def clean_document_type(self):
        document_type = self.cleaned_data.get('document_type').strip()
        
        # Solo validar si el valor ha cambiado
        if hasattr(self.instance, 'document_type') and document_type == self.instance.document_type:
            return document_type
            
        # Validación de existencia (case insensitive)
        queryset = DocumentType.objects.filter(document_type__iexact=document_type)
        
        if self.instance and self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)
        
        if queryset.exists():
            raise ValidationError("Ya existe un tipo de documento con este nombre.")
        
        return document_type
    

class SpecialtiesForm(forms.ModelForm):
    specialties = forms.CharField(
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej: Medicina General, Pediatría, Cardiología'
        }),
        label='Tipo de Especialidad',
        help_text='Ingrese un nombre único para el tipo de especialidad'
    )
    class Meta:
        model = Specialties
        fields = ['specialties']
        error_messages = {
            'specialties': {
                'unique': "Este tipo de especialidad ya existe.",
            }
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.error_messages = {
                'required': f'El campo {field.label} es obligatorio',
            }


class AccessLevelForm(forms.ModelForm):
    access_level = forms.CharField(
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej: Administrador, Usuario, Medico'
        }),
        label='Nivel de Acceso',
        help_text='Ingrese un nombre único para el nivel de acceso'
    )
    class Meta:
        model = AccessLevel
        fields = ['access_level']
        error_messages = {
            'access_level': {
                'unique': "Este nombre de nuvel de acceso ya existe.",
            }
        }

class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Personalizar los campos sin eliminar el help_text predeterminado
        self.fields['old_password'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Contraseña actual'
        })
        self.fields['new_password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Nueva contraseña'
        })
        self.fields['new_password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirmar nueva contraseña'
        })