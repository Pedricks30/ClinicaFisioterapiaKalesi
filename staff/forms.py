from django import forms
from .models import Staff
from users.models import DocumentType, Specialties

class StaffForm(forms.ModelForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
        label="Correo electrónico"
    )
    name = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label='Nombre completo'
    )
    phone_number = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'phone'}),
        label='Número de teléfono'
    )
    address1 = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label='Dirección'
    )
    document_number = forms.CharField(
        max_length=40,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label='Número de documento'
    )
    sex = forms.ChoiceField(
        choices=[('Masculino', 'Masculino'), ('Femenino', 'Femenino')],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Sexo'
    )
    birthdate = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        label='Fecha de nacimiento'
    )
    profile_image = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'}),
        label='Imagen de perfil'
    )
    document_type = forms.ModelChoiceField(
        queryset=DocumentType.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Tipo de documento'
    )
    specialties = forms.ModelChoiceField(
        queryset=Specialties.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Especialidad'
    )

    class Meta:
        model = Staff
        fields = '__all__'  # Aquí se usa '__all__' para incluir todos los campos del modelo
        widgets = {
            'profile_image': forms.FileInput(attrs={'class': 'd-none'})  # Ocultamos el input original
        }
        
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if not isinstance(field.widget, forms.FileInput):
                field.widget.attrs['class'] = field.widget.attrs.get('class', '') + ' form-control'
            if field_name == 'profile_image':
                field.widget.attrs['class'] = 'form-control-file'