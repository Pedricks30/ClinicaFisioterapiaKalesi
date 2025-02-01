from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, DocumentType, AccessLevel

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Correo electrónico'})
    )
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre'})
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apellido'})
    )
    age = forms.IntegerField(
        required=True,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Edad'})
    )
    phone = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Teléfono'})
    )
    prefijo_telefono = forms.CharField(
        max_length=5,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Prefijo'})
    )
    direccion1 = forms.CharField(
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Dirección 1'})
    )
    direccion2 = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Dirección 2'})
    )
    pais = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'País'})
    )
    fecha_nacimiento = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    tipo_documento = forms.ModelChoiceField(
        queryset=DocumentType.objects.all(),
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    numero_documento = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Número de documento'})
    )
    nivel_acceso = forms.ModelChoiceField(
        queryset=AccessLevel.objects.all(),
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    # Personalizar el campo is_active
    is_active = forms.ChoiceField(
        choices=[(True, 'Activo'), (False, 'Inactivo')],  # Opciones para el combo box
        required=True,
        initial=True,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Activo",  # Etiqueta del campo
        help_text="Indica si el usuario debe ser tratado como activo. Desmarque esta opción en lugar de borrar la cuenta."
    )

    class Meta:
        model = CustomUser
        fields = (
            'username', 'email', 'first_name', 'last_name', 'age', 'phone', 'prefijo_telefono',
            'direccion1', 'direccion2', 'pais', 'fecha_nacimiento', 'tipo_documento', 'numero_documento',
            'nivel_acceso', 'password1', 'password2', 'is_active'
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Aplicar clases de Bootstrap a todos los campos
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})