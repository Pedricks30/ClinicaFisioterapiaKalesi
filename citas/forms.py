from django import forms
from .models import Cita
from paciente.models import Patient
from horario.models import Horario

class CitaForm(forms.ModelForm):
    paciente = forms.ModelChoiceField(
        queryset=Patient.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control select2'})
    )
    
    horario = forms.ModelChoiceField(
        queryset=Horario.objects.none(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Cita
        fields = ['paciente', 'fecha', 'hora_inicio', 'hora_fin', 'motivo', 'estado']
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'hora_inicio': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'hora_fin': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'motivo': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'estado': forms.Select(attrs={'class': 'form-control'})
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            self.fields['horario'].queryset = Horario.objects.filter(
                profesional=user
            )