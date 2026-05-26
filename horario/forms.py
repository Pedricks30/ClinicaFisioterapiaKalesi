# horarios/forms.py
from datetime import datetime, date, timedelta
from django import forms
from django.core.exceptions import ValidationError
from django.db.models import Q
from .models import Horario
from users.models import CustomUser, Specialties
from medical.models import Medico
from physiotherapist.models import Fisioterapeuta


class HorarioForm(forms.ModelForm):
    """
    Formulario para crear/editar horarios de profesionales.
    """
    
    dias_laborables = forms.MultipleChoiceField(
        choices=Horario.DIAS_SEMANA,
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label='Días Laborables',
        error_messages={'required': 'Debe seleccionar al menos un día laborable.'}
    )
    
    hora_inicio = forms.TimeField(
        widget=forms.TimeInput(attrs={
            'type': 'time',
            'class': 'form-control',
            'min': '06:00',
            'max': '22:00'
        }),
        label='Hora de Inicio',
        error_messages={'required': 'La hora de inicio es obligatoria.'}
    )
    
    hora_fin = forms.TimeField(
        widget=forms.TimeInput(attrs={
            'type': 'time',
            'class': 'form-control',
            'min': '06:00',
            'max': '22:00'
        }),
        label='Hora de Fin',
        error_messages={'required': 'La hora de fin es obligatoria.'}
    )
    
    # Campo disponible como ChoiceField (sin modificar el modelo)
    disponible = forms.ChoiceField(
        choices=[(True, 'Disponible'), (False, 'No disponible')],
        required=True,
        initial=True,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Estado del Horario',
        help_text="Seleccione 'Disponible' para activar el horario o 'No disponible' para desactivarlo temporalmente."
    )
    
    especialidad = forms.ModelChoiceField(
        queryset=Specialties.objects.all().order_by('specialties'),
        required=True,
        label="Especialidad",
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'id_especialidad',
        }),
        error_messages={'required': 'Debe seleccionar una especialidad.'}
    )

    profesional = forms.ModelChoiceField(
        queryset=CustomUser.objects.none(),
        required=True,
        label="Profesional",
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'id_profesional',
        }),
        error_messages={'required': 'Debe seleccionar un profesional.'}
    )

    class Meta:
        model = Horario
        fields = ['especialidad', 'profesional', 'dias_laborables', 'hora_inicio', 'hora_fin', 'disponible']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # ================================================================
        # MODO EDICIÓN: Bloquear especialidad y profesional (solo lectura)
        # ================================================================
        if self.instance and self.instance.pk:
            profesional = self.instance.profesional
            perfil = profesional.perfil_profesional
            
            # --- CAMPO PROFESIONAL (SOLO LECTURA) ---
            self.fields['profesional'].queryset = CustomUser.objects.filter(pk=profesional.pk)
            self.fields['profesional'].initial = profesional
            self.fields['profesional'].disabled = True
            self.fields['profesional'].widget.attrs.update({
                'class': 'form-control bg-gray',
            })
            self.fields['profesional'].help_text = '⚠️ El profesional no se puede modificar en la edición.'
            
            # --- CAMPO ESPECIALIDAD (SOLO LECTURA) ---
            if perfil and perfil.specialties:
                self.fields['especialidad'].queryset = Specialties.objects.filter(pk=perfil.specialties.pk)
                self.fields['especialidad'].initial = perfil.specialties
                self.fields['especialidad'].disabled = True
                self.fields['especialidad'].widget.attrs.update({
                    'class': 'form-control bg-gray',
                })
                self.fields['especialidad'].help_text = '⚠️ La especialidad no se puede modificar en la edición.'
            
            # Precargar días laborables desde la instancia
            if self.instance.dias_semana:
                self.initial['dias_laborables'] = self.instance.dias_semana.split(',')
            
            # Precargar el valor de disponible (convertir a string para el ChoiceField)
            self.initial['disponible'] = str(self.instance.disponible)
        
        # ================================================================
        # MODO CREACIÓN: Cargar profesionales dinámicamente
        # ================================================================
        else:
            # Si ya hay datos POST y se seleccionó especialidad
            if 'especialidad' in self.data:
                try:
                    especialidad_id = int(self.data.get('especialidad'))
                    if especialidad_id:
                        self.fields['profesional'].queryset = self._get_profesionales_por_especialidad(especialidad_id)
                        # No deshabilitar el campo profesional
                        self.fields['profesional'].widget.attrs.pop('disabled', None)
                except (ValueError, TypeError):
                    pass
            else:
                # Sin datos POST, mostrar mensaje en el select
                self.fields['profesional'].widget.attrs['disabled'] = 'disabled'
                self.fields['profesional'].help_text = 'Seleccione primero una especialidad para ver los profesionales disponibles.'

    def _get_profesionales_por_especialidad(self, especialidad_id):
        """
        Busca profesionales (MEDIC y FISIO) que tengan la especialidad indicada.
        """
        medicos_ids = Medico.objects.filter(
            specialties_id=especialidad_id
        ).values_list('user_id', flat=True)
        
        fisios_ids = Fisioterapeuta.objects.filter(
            specialties_id=especialidad_id
        ).values_list('user_id', flat=True)
        
        todos_ids = list(medicos_ids) + list(fisios_ids)
        
        return CustomUser.objects.filter(
            id__in=todos_ids,
            tipo_usuario__in=['MEDIC', 'FISIO']
        ).order_by('first_name', 'last_name')

    def clean_hora_inicio(self):
        hora_inicio = self.cleaned_data.get('hora_inicio')
        if hora_inicio:
            # Validar que esté en horario laboral (6:00 - 22:00)
            if hora_inicio < datetime.strptime('06:00', '%H:%M').time():
                raise ValidationError("La hora de inicio no puede ser antes de las 06:00.")
            if hora_inicio > datetime.strptime('22:00', '%H:%M').time():
                raise ValidationError("La hora de inicio no puede ser después de las 22:00.")
        return hora_inicio

    def clean_hora_fin(self):
        hora_fin = self.cleaned_data.get('hora_fin')
        if hora_fin:
            if hora_fin < datetime.strptime('06:00', '%H:%M').time():
                raise ValidationError("La hora de fin no puede ser antes de las 06:00.")
            if hora_fin > datetime.strptime('22:00', '%H:%M').time():
                raise ValidationError("La hora de fin no puede ser después de las 22:00.")
        return hora_fin

    def clean_dias_laborables(self):
        dias = self.cleaned_data.get('dias_laborables', [])
        if not dias:
            raise ValidationError("Debe seleccionar al menos un día laborable.")
        return dias

    def clean(self):
        cleaned_data = super().clean()
        profesional = cleaned_data.get('profesional')
        especialidad = cleaned_data.get('especialidad')
        hora_inicio = cleaned_data.get('hora_inicio')
        hora_fin = cleaned_data.get('hora_fin')
        dias_laborables = cleaned_data.get('dias_laborables', [])
        
        # Validar que el profesional y especialidad estén presentes
        if not self.instance.pk:  # Solo en creación
            if not especialidad:
                self.add_error('especialidad', "Debe seleccionar una especialidad.")
            if not profesional:
                self.add_error('profesional', "Debe seleccionar un profesional.")
        
        # Validar horas
        if hora_inicio and hora_fin:
            if hora_inicio >= hora_fin:
                self.add_error('hora_fin', "La hora de fin debe ser posterior a la hora de inicio.")
            else:
                # Validar duración mínima de 15 minutos
                inicio_dt = datetime.combine(date.today(), hora_inicio)
                fin_dt = datetime.combine(date.today(), hora_fin)
                diferencia = fin_dt - inicio_dt
                if diferencia < timedelta(minutes=15):
                    self.add_error('hora_fin', "El horario debe tener al menos 15 minutos de duración.")
                    
        # Validar solapamiento de días y horas con otros horarios del profesional
        if profesional and dias_laborables and hora_inicio and hora_fin:
            # Excluir la instancia actual si estamos editando
            existing_horarios = Horario.objects.filter(profesional=profesional)
            if self.instance.pk:
                existing_horarios = existing_horarios.exclude(pk=self.instance.pk)

            # Verificar solapamientos
            dias_seleccionados = set(dias_laborables)

            for horario in existing_horarios:
                dias_existentes = set(horario.dias_semana.split(','))
                dias_comunes = dias_seleccionados & dias_existentes

                if dias_comunes:
                    # Verificar si hay solapamiento de horas
                    if (hora_inicio < horario.hora_fin and hora_fin > horario.hora_inicio):
                        dias_str = ', '.join([dict(Horario.DIAS_SEMANA)[d] for d in dias_comunes])
                        self.add_error('dias_laborables',
                            f'El horario solapa con otro existente en los días: {dias_str}. '
                            f'Horario existente: {horario.hora_inicio} - {horario.hora_fin}'
                        )
                        break
        # Validar solapamiento de días con otros horarios del profesional
        '''if profesional and dias_laborables:
            # Excluir la instancia actual si estamos editando
            existing_horarios = Horario.objects.filter(profesional=profesional)
            if self.instance.pk:
                existing_horarios = existing_horarios.exclude(pk=self.instance.pk)
            
            # Verificar cada día seleccionado
            dias_solapados = []
            for dia in dias_laborables:
                for horario in existing_horarios:
                    dias_existentes = horario.dias_semana.split(',')
                    if dia in dias_existentes:
                        dias_solapados.append(dict(Horario.DIAS_SEMANA)[dia])
                        break
            
            if dias_solapados:
                dias_str = ', '.join(dias_solapados)
                self.add_error('dias_laborables', 
                    f"El profesional ya tiene horario asignado los siguientes días: {dias_str}. "
                    "Seleccione días diferentes o edite el horario existente."
                ) '''
        
        # Validar que no exista otro horario para el mismo profesional (solo en creación)
        #if not self.instance.pk and profesional:
        #   if Horario.objects.filter(profesional=profesional).exists():
        #        self.add_error('profesional', 
        #            "Este profesional ya tiene un horario asignado. "
        #            "Solo se permite un horario por profesional. Edite el horario existente si necesita cambios."
        #        )
        
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        dias_laborables = self.cleaned_data.get('dias_laborables', [])
        instance.dias_semana = ','.join(dias_laborables) if dias_laborables else ''
        
        # Convertir el valor del ChoiceField a booleano para el modelo
        disponible_value = self.cleaned_data.get('disponible')
        if disponible_value == 'True' or disponible_value == True:
            instance.disponible = True
        else:
            instance.disponible = False
        
        if commit:
            instance.save()
        
        return instance