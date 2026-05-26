from django import forms
from django.utils import timezone
from datetime import datetime, timedelta
from django.core.exceptions import ValidationError
from .models import Cita
from horario.models import Horario
from users.models import CustomUser, Specialties
from paciente.models import Patient
from medical.models import Medico
from physiotherapist.models import Fisioterapeuta


class CitaModalForm(forms.ModelForm):
    """
    Formulario que se muestra en el modal del calendario.
    Campos simplificados para crear/editar citas rápidamente.
    """
    
    paciente = forms.ModelChoiceField(
        queryset=Patient.objects.filter(estado=True).order_by('apellidos', 'nombres'),
        required=True,
        label="Paciente",
        widget=forms.Select(attrs={
            'class': 'form-control select2-buscar',
            'data-placeholder': 'Buscar paciente por nombre o documento...'
        })
    )
    
    motivo = forms.CharField(
        required=True,
        label="Motivo de la cita",
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2,
            'placeholder': 'Describa el motivo de la consulta...'
        })
    )
    
    color = forms.CharField(
        required=False,
        label="Color en calendario",
        initial='#007BFF',
        widget=forms.TextInput(attrs={
            'type': 'color',
            'class': 'form-control form-control-color',
            'style': 'width: 60px; height: 40px; padding: 5px;'
        })
    )
    
    fecha = forms.DateTimeField(
        required=True,
        label="Fecha y hora",
        widget=forms.DateTimeInput(attrs={
            'type': 'datetime-local',
            'class': 'form-control',
            'id': 'id_fecha_cita'
        })
    )
    
    duracion = forms.IntegerField(
        required=True,
        initial=30,
        min_value=15,
        label="Duración (minutos)",
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': '15',
            'step': '15',
            'id': 'id_duracion_cita'
        })
    )

    class Meta:
        model = Cita
        fields = ['paciente', 'motivo', 'color', 'fecha', 'duracion']

    def __init__(self, *args, **kwargs):
        self.profesional = kwargs.pop('profesional', None)
        self.creada_por = kwargs.pop('creada_por', None)
        super().__init__(*args, **kwargs)

    def clean_fecha(self):
        fecha = self.cleaned_data.get('fecha')
        if fecha and fecha < timezone.now():
            raise ValidationError("No se pueden agendar citas en fechas pasadas.")
        return fecha

    def clean(self):
        cleaned_data = super().clean()
        fecha = cleaned_data.get('fecha')
        duracion = cleaned_data.get('duracion')
        
        if fecha and duracion and self.profesional:
            # Validar solapamiento
            fin_cita = fecha + timedelta(minutes=duracion)
            citas_solapadas = Cita.objects.filter(
                profesional=self.profesional,
                fecha__lt=fin_cita,
                fecha__gte=fecha - timedelta(minutes=duracion),
                estado__in=['PENDIENTE', 'CONFIRMADA', 'EN_PROCESO']
            )
            if self.instance and self.instance.pk:
                citas_solapadas = citas_solapadas.exclude(pk=self.instance.pk)
            
            if citas_solapadas.exists():
                raise ValidationError(
                    f"El profesional ya tiene una cita en ese horario: "
                    f"{citas_solapadas.first().paciente} a las "
                    f"{citas_solapadas.first().fecha.strftime('%H:%M')}"
                )
        
        return cleaned_data

    def save(self, commit=True):
        cita = super().save(commit=False)
        if self.profesional:
            cita.profesional = self.profesional
        if self.creada_por:
            cita.creada_por = self.creada_por
        cita.estado = 'PENDIENTE'
        
        if commit:
            cita.save()
        return cita


class BusquedaCitaForm(forms.Form):
    """
    Formulario de búsqueda general de citas.
    """
    q = forms.CharField(
        required=False,
        label="Buscar",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar por nombre de médico, paciente, motivo...',
            'id': 'id_busqueda_citas'
        })
    )
    
    estado = forms.ChoiceField(
        choices=[('', 'Todos')] + list(Cita.ESTADO_CHOICES),
        required=False,
        label="Estado",
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'id_estado_filtro'
        })
    )
    
    fecha_desde = forms.DateField(
        required=False,
        label="Fecha desde",
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
            'id': 'id_fecha_desde'
        })
    )
    
    fecha_hasta = forms.DateField(
        required=False,
        label="Fecha hasta",
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
            'id': 'id_fecha_hasta'
        })
    )