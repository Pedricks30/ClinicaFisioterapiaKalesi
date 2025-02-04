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
    telephone_prefix = forms.CharField(  # Cambiado a telephone_prefix
        max_length=5,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Prefijo'})
    )
    address1 = forms.CharField(  # Cambiado a address1
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Dirección 1'})
    )
    address2 = forms.CharField(  # Cambiado a address2
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Dirección 2'})
    )
    country = forms.CharField(  # Cambiado a country
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'País'})
    )
    birthdate = forms.DateField(  # Cambiado a birthdate
        required=True,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    document_type = forms.ModelChoiceField(  # Cambiado a document_type
        queryset=DocumentType.objects.all(),
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    document_number = forms.CharField(  # Cambiado a document_number
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Número de documento'})
    )
    access_level = forms.ModelChoiceField(  # Cambiado a access_level
        queryset=AccessLevel.objects.all(),
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    profile_image = forms.ImageField(  # Agregado el campo profile_image
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control'}),
        label="Imagen de perfil"
    )
    is_active = forms.ChoiceField(
        choices=[(True, 'Activo'), (False, 'Inactivo')],
        required=True,
        initial=True,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Activo",
        help_text="Indica si el usuario debe ser tratado como activo. Desmarque esta opción en lugar de borrar la cuenta."
    )

    class Meta:
        model = CustomUser
        fields = (
            'username', 'email', 'first_name', 'last_name', 'age', 'phone', 'telephone_prefix',
            'address1', 'address2', 'country', 'birthdate', 'document_type', 'document_number',
            'access_level', 'password1', 'password2', 'is_active', 'profile_image'
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Aplicar clases de Bootstrap a todos los campos
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})