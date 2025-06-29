from django import forms
from django.core.exceptions import ValidationError
from .models import MedicalUser, DocumentType, Specialties

class MedicalUserForm(forms.ModelForm):
    name = forms.CharField(
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label='Nombre Completo'
    )
    sexo = forms.ChoiceField(
        choices=MedicalUser.SEXO_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Sexo'
    )
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
        label='Correo Electrónico'
    )
    address1 = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label='Dirección Domicilio'
    )
    document_type = forms.ModelChoiceField(
        queryset=DocumentType.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Tipo Documento'
    )
    phone_number = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'phone'}),
        label='Teléfono'
    )
    document_number = forms.CharField(
        max_length=40,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label='Número Documento'
    )
    country = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'country'}),
        label='Nacionalidad'
    )
    birthdate = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        label='Fecha de Nacimiento'
    )
    specialties = forms.ModelChoiceField(
        queryset=Specialties.objects.all(),
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Especialidad'
    )
    class Meta:
        model = MedicalUser
        fields = [
            'name',
            'sexo',
            'email',
            'address1',
            'document_type',
            'phone_number',
            'document_number',
            'country',
            'birthdate',
            'specialties',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if self.instance and self.instance.email == email:
            return email
        if MedicalUser.objects.filter(email=email).exists():
            raise ValidationError("Ya existe un profesional con este correo electrónico.")
        return email

    def clean_document_number(self):
        document_number = self.cleaned_data.get('document_number')
        if self.instance and self.instance.document_number == document_number:
            return document_number
        if MedicalUser.objects.filter(document_number=document_number).exists():
            raise ValidationError("Ya existe un profesional con este número de documento.")
        return document_number