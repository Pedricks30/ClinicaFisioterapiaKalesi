from datetime import datetime, date
from django import forms
from django.core.exceptions import ValidationError
from .models import Horario
from medical.models import MedicalUser, Specialties

class HorarioForm(forms.ModelForm):
    dias_laborables = forms.MultipleChoiceField(
        choices=Horario.DIAS_SEMANA,
        widget=forms.CheckboxSelectMultiple,
        required=True,
        error_messages={
            'required': 'Debe seleccionar al menos un día laborable.',
            'invalid_choice': 'Seleccione días válidos.'
        }
    )
    
    hora_inicio = forms.TimeField(
        widget=forms.TimeInput(attrs={
            'type': 'time',
            'class': 'form-control',
            'min': '06:00',
            'max': '22:00'
        }),
        error_messages={
            'required': 'La hora de inicio es obligatoria.',
            'invalid': 'Ingrese una hora válida.'
        }
    )
    
    hora_fin = forms.TimeField(
        widget=forms.TimeInput(attrs={
            'type': 'time',
            'class': 'form-control',
            'min': '06:00',
            'max': '22:00'
        }),
        error_messages={
            'required': 'La hora de fin es obligatoria.',
            'invalid': 'Ingrese una hora válida.'
        }
    )
    
    especialidad = forms.ModelChoiceField(
        queryset=Specialties.objects.all(),
        required=True,
        label="Especialidad",
        widget=forms.Select(attrs={
            'class': 'form-control select2',
            'hx-get': '',
            'hx-target': '#id_profesional',
            'hx-trigger': 'change',
            'data-placeholder': 'Seleccione una especialidad'
        }),
        error_messages={
            'required': 'Debe seleccionar una especialidad.',
            'invalid_choice': 'Seleccione una especialidad válida.'
        }
    )

    profesional = forms.ModelChoiceField(
        queryset=MedicalUser.objects.none(),
        required=True,
        label="Profesional",
        widget=forms.Select(attrs={
            'class': 'form-control select2',
            'disabled': 'disabled',
            'data-placeholder': 'Primero seleccione una especialidad'
        }),
        error_messages={
            'required': 'Debe seleccionar un profesional.',
            'invalid_choice': 'Seleccione un profesional válido.'
        }
    )

    class Meta:
        model = Horario
        fields = ['especialidad', 'profesional', 'dias_laborables', 'hora_inicio', 'hora_fin']
        labels = {
            'dias_laborables': 'Días Laborables',
            'hora_inicio': 'Hora de Inicio',
            'hora_fin': 'Hora de Fin'
        }

    def __init__(self, *args, **kwargs):
        especialidad_filter = kwargs.pop('especialidad_filter', None)
        profesional_filter = kwargs.pop('profesional_filter', None)
        
        super().__init__(*args, **kwargs)
        
        # Configurar especialidad
        self.fields['especialidad'].queryset = Specialties.objects.all().order_by('specialties')
        if especialidad_filter:
            self.fields['especialidad'].initial = especialidad_filter
        
        # Configurar profesional
        queryset = MedicalUser.objects.none()
        
        # Si viene de un filtro, cargar los profesionales correspondientes
        if especialidad_filter:
            queryset = MedicalUser.objects.filter(
                specialties__id_specialty=especialidad_filter
            ).order_by('name')
            
            if profesional_filter:
                queryset = queryset.filter(name__icontains=profesional_filter)
        
        # Si es una edición y tiene profesional asociado
        if self.instance and hasattr(self.instance, 'profesional') and self.instance.profesional:
            queryset = MedicalUser.objects.filter(pk=self.instance.profesional.pk)
            if not self.fields['especialidad'].initial and self.instance.profesional.specialties:
                self.fields['especialidad'].initial = self.instance.profesional.specialties.id_specialty
        
        # Habilitar campo profesional si hay especialidad seleccionada
        if 'especialidad' in self.data:
            try:
                especialidad_id = int(self.data.get('especialidad'))
                queryset = MedicalUser.objects.filter(
                    specialties__id_specialty=especialidad_id
                ).order_by('name')
                self.fields['profesional'].widget.attrs.pop('disabled', None)
            except (ValueError, TypeError):
                pass
        
        self.fields['profesional'].queryset = queryset

        # Establecer días laborables iniciales si existe la instancia
        if self.instance and self.instance.dias_laborables:
            self.initial['dias_laborables'] = self.instance.dias_laborables.split(',')

    def clean_dias_laborables(self):
        dias = self.cleaned_data.get('dias_laborables', [])
        if not dias:
            raise ValidationError("Debe seleccionar al menos un día laborable.")
        
        # Validar que los días seleccionados sean válidos
        dias_validos = [choice[0] for choice in Horario.DIAS_SEMANA]
        for dia in dias:
            if dia not in dias_validos:
                raise ValidationError(f"'{dia}' no es un día válido.")
        
        return ','.join(dias)

    def clean_profesional(self):
        especialidad = self.cleaned_data.get('especialidad')
        profesional = self.cleaned_data.get('profesional')
        
        if profesional and especialidad:
            # Verificar si el profesional tiene la especialidad seleccionada
            if not (profesional.specialties and profesional.specialties.id_specialty == especialidad.id_specialty):
                raise ValidationError("El profesional seleccionado no pertenece a la especialidad elegida.")
        
        return profesional

    def clean(self):
        cleaned_data = super().clean()
        hora_inicio = cleaned_data.get('hora_inicio')
        hora_fin = cleaned_data.get('hora_fin')
        dias_laborables = cleaned_data.get('dias_laborables')
        
        # Validación de horarios
        if hora_inicio and hora_fin:
            # Validar que la hora fin sea mayor que la hora inicio
            if hora_inicio >= hora_fin:
                self.add_error('hora_fin', "La hora de fin debe ser posterior a la hora de inicio.")
            
            # Validar duración mínima de 15 minutos
            try:
                inicio = datetime.combine(date.today(), hora_inicio)
                fin = datetime.combine(date.today(), hora_fin)
                diferencia = fin - inicio
                
                if diferencia.total_seconds() < 900:
                    self.add_error('hora_fin', "El horario debe tener al menos 15 minutos de duración.")
                
                # Validar horario máximo (12 horas)
                if diferencia.total_seconds() > 43200:
                    self.add_error('hora_fin', "El horario no puede exceder las 12 horas de duración.")
            
            except Exception as e:
                self.add_error(None, f"Error al validar los horarios: {str(e)}")
        
        # Validación de especialidad y profesional
        especialidad = cleaned_data.get('especialidad')
        profesional = cleaned_data.get('profesional')
        
        if especialidad and not profesional:
            self.add_error('profesional', "Debe seleccionar un profesional de la especialidad elegida.")
        elif profesional and not especialidad:
            self.add_error('especialidad', "Debe seleccionar una especialidad para el profesional.")
        
        # Validación de días laborables
        if dias_laborables and isinstance(dias_laborables, str):
            dias = dias_laborables.split(',')
            if len(dias) > 7:
                self.add_error('dias_laborables', "No puede seleccionar más de 7 días.")
        
        return cleaned_data