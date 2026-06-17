# citas/forms.py
from django import forms
from django.utils import timezone
from datetime import datetime, timedelta
from django.core.exceptions import ValidationError
from .models import Cita
from horario.models import Horario
from users.models import CustomUser
from paciente.models import Patient


class CitaModalForm(forms.ModelForm):
    """
    Formulario que se muestra en el modal del calendario.
    El tipo de cita se selecciona manualmente.
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
    
    # ✅ NUEVO: Campo tipo_cita manual
    tipo_cita = forms.ChoiceField(
        choices=Cita.TIPO_CITA_FISIOTERAPIA,
        required=True,
        label="Tipo de Cita",
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'id_tipo_cita'
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
        input_formats=['%Y-%m-%dT%H:%M', '%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S'],
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
        fields = ['paciente', 'motivo', 'tipo_cita', 'color', 'fecha', 'duracion']  # ✅ Agregar tipo_cita

    def __init__(self, *args, **kwargs):
        self.profesional = kwargs.pop('profesional', None)
        self.creada_por = kwargs.pop('creada_por', None)
        self.forzar_finalizacion = kwargs.pop('forzar_finalizacion', False)
        super().__init__(*args, **kwargs)
        
        # ✅ Si es edición, deshabilitar el campo tipo_cita
        if self.instance and self.instance.pk:
            self.fields['tipo_cita'].disabled = True
            self.fields['tipo_cita'].widget.attrs['disabled'] = 'disabled'

    def clean_fecha(self):
        fecha = self.cleaned_data.get('fecha')
        if fecha and fecha < timezone.now():
            raise ValidationError("No se pueden agendar citas en fechas pasadas.")
        return fecha

    def clean_tipo_cita(self):
        """Validar que el tipo_cita sea válido"""
        tipo_cita = self.cleaned_data.get('tipo_cita')
        tipos_validos = [t[0] for t in Cita.TIPO_CITA_FISIOTERAPIA]
        if tipo_cita not in tipos_validos:
            raise ValidationError("Tipo de cita no válido.")
        return tipo_cita

    def clean(self):
        cleaned_data = super().clean()
        fecha = cleaned_data.get('fecha')
        duracion = cleaned_data.get('duracion')
        paciente = cleaned_data.get('paciente')
        tipo_cita = cleaned_data.get('tipo_cita')

        # Validar solapamiento
        if fecha and duracion and self.profesional:
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

        # Validar citas pendientes del paciente (excepto si es edición o finalización forzada)
        if paciente and self.profesional and not self.forzar_finalizacion:
            citas_pendientes = Cita.objects.filter(
                paciente=paciente,
                profesional=self.profesional,
                estado__in=['PENDIENTE', 'CONFIRMADA', 'EN_PROCESO']
            ).exclude(pk=self.instance.pk if self.instance else None)

            if citas_pendientes.exists():
                raise ValidationError(
                    f"El paciente tiene {citas_pendientes.count()} cita(s) pendiente(s). "
                    "Debe completar o cancelar las citas existentes antes de crear nuevas."
                )

        # ✅ Validar que no se pueda crear una PRIMERA_CONSULTA si ya existe
        if tipo_cita == 'PRIMERA_CONSULTA' and paciente and not self.forzar_finalizacion:
            existe_primera = Cita.objects.filter(
                paciente=paciente,
                profesional=self.profesional,
                tipo_cita='PRIMERA_CONSULTA',
                estado__in=['PENDIENTE', 'CONFIRMADA', 'COMPLETADA']
            ).exclude(pk=self.instance.pk if self.instance else None).exists()
            
            if existe_primera:
                raise ValidationError(
                    "Este paciente ya tiene una Primera Consulta registrada. "
                    "Solo puede tener una PRIMERA_CONSULTA."
                )

        # ✅ Validar FINALIZACION
        if tipo_cita == 'FINALIZACION' and paciente and not self.forzar_finalizacion:
            # Verificar que tenga primera consulta
            tiene_primera = Cita.objects.filter(
                paciente=paciente,
                profesional=self.profesional,
                tipo_cita='PRIMERA_CONSULTA',
                estado='COMPLETADA'
            ).exists()
            
            if not tiene_primera:
                raise ValidationError(
                    "El paciente debe tener una Primera Consulta completada antes de finalizar."
                )
            
            # Verificar que tenga al menos un seguimiento
            tiene_seguimiento = Cita.objects.filter(
                paciente=paciente,
                profesional=self.profesional,
                tipo_cita='SEGUIMIENTO',
                estado='COMPLETADA'
            ).exists()
            
            if not tiene_seguimiento:
                raise ValidationError(
                    "El paciente debe tener al menos una sesión de Seguimiento completada antes de finalizar."
                )
            
            # Verificar que no tenga ya una finalización
            tiene_finalizacion = Cita.objects.filter(
                paciente=paciente,
                profesional=self.profesional,
                tipo_cita='FINALIZACION',
                estado__in=['PENDIENTE', 'CONFIRMADA', 'COMPLETADA']
            ).exclude(pk=self.instance.pk if self.instance else None).exists()
            
            if tiene_finalizacion:
                raise ValidationError(
                    "Este paciente ya tiene una Finalización registrada."
                )

        # ✅ Validar SEGUIMIENTO
        if tipo_cita == 'SEGUIMIENTO' and paciente:
            tiene_primera = Cita.objects.filter(
                paciente=paciente,
                profesional=self.profesional,
                tipo_cita='PRIMERA_CONSULTA',
                estado='COMPLETADA'
            ).exists()
            
            if not tiene_primera:
                raise ValidationError(
                    "El paciente debe tener una Primera Consulta completada antes de crear seguimientos."
                )

        return cleaned_data

    def save(self, commit=True):
        # Crear la instancia con los datos del formulario
        cita = super().save(commit=False)
        
        # Asignar otros campos
        if self.profesional:
            cita.profesional = self.profesional
        if self.creada_por:
            cita.creada_por = self.creada_por
        cita.estado = 'PENDIENTE'

        # ✅ El tipo_cita ya viene del formulario, no se asigna automáticamente
        # Solo se forza si viene de finalización
        if self.forzar_finalizacion:
            cita.tipo_cita = 'FINALIZACION'
            cita.motivo = 'Finalización del tratamiento'

        # Calcular número de sesión (solo para nuevas citas)
        if not self.instance.pk:
            if cita.tipo_cita == 'SEGUIMIENTO':
                sesiones_completadas = Cita.objects.filter(
                    paciente=cita.paciente,
                    profesional=self.profesional,
                    tipo_cita='SEGUIMIENTO',
                    estado='COMPLETADA'
                ).count()
                cita.numero_sesion = sesiones_completadas + 1
            elif cita.tipo_cita == 'PRIMERA_CONSULTA':
                cita.numero_sesion = 1

        if commit:
            try:
                cita.save()
            except ValidationError as e:
                if hasattr(e, 'error_dict'):
                    for field, errors in e.error_dict.items():
                        for error in errors:
                            self.add_error(field, error)
                else:
                    self.add_error(None, str(e))
                raise
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