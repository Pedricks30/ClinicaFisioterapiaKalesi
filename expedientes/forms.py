# expedientes/forms.py
from django import forms
from django.utils import timezone
from datetime import timedelta
from .models import PrimeraConsulta, ConsultaSegumiento, ConsultaFinalizacion
from .widgets import SiNoEspecificacionWidget


class BaseExpedienteForm(forms.ModelForm):
    """Formulario base con validación de tiempo de edición"""
    
    def __init__(self, *args, **kwargs):
        self.usuario = kwargs.pop('usuario', None)
        self.es_edicion = kwargs.pop('es_edicion', False)
        super().__init__(*args, **kwargs)
        
        # Configurar clases CSS para todos los campos
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.Textarea):
                field.widget.attrs['class'] = 'form-control'
                field.widget.attrs['rows'] = 3
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs['class'] = 'form-control select2'
            elif isinstance(field.widget, forms.NumberInput):
                field.widget.attrs['class'] = 'form-control'
            elif isinstance(field.widget, forms.TextInput):
                field.widget.attrs['class'] = 'form-control'
            elif isinstance(field.widget, forms.FileInput):
                field.widget.attrs['class'] = 'form-control-file'
    
    def clean(self):
        cleaned_data = super().clean()
        
        # Validar tiempo de edición (solo 1 hora después de creada)
        if self.es_edicion and self.instance.pk:
            tiempo_transcurrido = timezone.now() - self.instance.created_at
            if tiempo_transcurrido > timedelta(hours=1):
                raise forms.ValidationError(
                    "No se puede editar esta historia clínica. Solo tienes 1 hora después de crearla para hacer correcciones."
                )
        
        return cleaned_data


class PrimeraConsultaForm(forms.ModelForm):
    """Formulario para Primera Consulta"""
    
    class Meta:
        model = PrimeraConsulta
        exclude = ['created_at', 'updated_at', 'cita', 'profesional', 'expediente', 'fecha_consulta']
        widgets = {
            # Campos de texto grandes
            'motivo_consulta': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'diagnostico_fisioterapia': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'objetivos_tratamiento': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'plan_tratamiento': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'observaciones': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'localizacion_dolor': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'factores_agravantes': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'factores_atenuantes': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'tratamientos_previos': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'mecanismo_lesion': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            
            # Campos numéricos
            'peso': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'estatura': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'tipo_sangre': forms.Select(attrs={'class': 'form-control select2'}),
            'tipo_dolor': forms.TextInput(attrs={'class': 'form-control'}),
            'tiempo_evolucion': forms.TextInput(attrs={'class': 'form-control'}),
            'frecuencia_sesiones': forms.TextInput(attrs={'class': 'form-control'}),
            'numero_sesiones_recomendadas': forms.NumberInput(attrs={'class': 'form-control'}),
            'nivel_dolor_inicial': forms.HiddenInput(),
            
            # Campos goniométricos
            'ms_flexion_eval1_izq': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '°'}),
            'ms_flexion_eval1_der': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '°'}),
            'ms_extension_eval1_izq': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '°'}),
            'ms_extension_eval1_der': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '°'}),
            'ms_abduccion_eval1_izq': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '°'}),
            'ms_abduccion_eval1_der': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '°'}),
            'ms_flexion_eval2_izq': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '°'}),
            'ms_flexion_eval2_der': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '°'}),
            'ms_extension_eval2_izq': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '°'}),
            'ms_extension_eval2_der': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '°'}),
            'ms_abduccion_eval2_izq': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '°'}),
            'ms_abduccion_eval2_der': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '°'}),
            
            'mi_flexion_eval1_izq': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '°'}),
            'mi_flexion_eval1_der': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '°'}),
            'mi_extension_eval1_izq': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '°'}),
            'mi_extension_eval1_der': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '°'}),
            'mi_flexion_eval2_izq': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '°'}),
            'mi_flexion_eval2_der': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '°'}),
            'mi_extension_eval2_izq': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '°'}),
            'mi_extension_eval2_der': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '°'}),
            
            'tronco_flexion_eval1': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '°'}),
            'tronco_extension_eval1': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '°'}),
            'tronco_lateral_izq_eval1': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '°'}),
            'tronco_lateral_der_eval1': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '°'}),
            'tronco_flexion_eval2': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '°'}),
            'tronco_extension_eval2': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '°'}),
            'tronco_lateral_izq_eval2': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '°'}),
            'tronco_lateral_der_eval2': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '°'}),
            
            'cuello_flexion_eval1': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '°'}),
            'cuello_extension_eval1': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '°'}),
            'cuello_lateral_izq_eval1': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '°'}),
            'cuello_lateral_der_eval1': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '°'}),
            'cuello_rotacion_izq_eval1': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '°'}),
            'cuello_rotacion_der_eval1': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '°'}),
            'cuello_flexion_eval2': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '°'}),
            'cuello_extension_eval2': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '°'}),
            'cuello_lateral_izq_eval2': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '°'}),
            'cuello_lateral_der_eval2': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '°'}),
            'cuello_rotacion_izq_eval2': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '°'}),
            'cuello_rotacion_der_eval2': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '°'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Configurar clases CSS
        self.fields['peso'].widget.attrs['class'] = 'form-control'
        self.fields['estatura'].widget.attrs['class'] = 'form-control'
        self.fields['tipo_sangre'].widget.attrs['class'] = 'form-control select2'
        
        # Hacer que nivel_dolor_inicial sea opcional
        self.fields['nivel_dolor_inicial'].required = False
        
        # Campos obligatorios
        self.fields['motivo_consulta'].required = True
        self.fields['diagnostico_fisioterapia'].required = True
        
        # Campos que usan SiNoEspecificacionWidget
        campos_si_no = [
            'diabetes', 'alergias', 'hipertension', 'cancer', 'traumatismos_previos',
            'cirugias_previas', 'transfusiones_sanguineas', 'enf_reumaticas',
            'accidentes', 'cardiopatias', 'fracturas', 'espasmos_o_contracturas',
            'actividad_fisica', 'consumo_tabaco', 'consumo_alcohol', 'consumo_drogas',
            'automedicacion', 'esta_embarazada'
        ]
        
        for campo in campos_si_no:
            if campo in self.fields:
                self.fields[campo].widget = SiNoEspecificacionWidget(
                    etiqueta_si_no=self.fields[campo].label,
                    placeholder=f"Especifique detalles sobre {self.fields[campo].label.lower()}..."
                )
                self.fields[campo].required = False
        
        # Campos de evaluación muscular
        campos_musculares = [
            'ms_eval1_izquierda', 'ms_eval1_derecha', 'ms_eval2_izquierda', 'ms_eval2_derecha',
            'mi_eval1_izquierda', 'mi_eval1_derecha', 'mi_eval2_izquierda', 'mi_eval2_derecha',
            'tronco_eval1_izquierda', 'tronco_eval1_derecha', 'tronco_eval2_izquierda', 'tronco_eval2_derecha',
            'cuello_eval1_izquierda', 'cuello_eval1_derecha', 'cuello_eval2_izquierda', 'cuello_eval2_derecha'
        ]
        
        for campo in campos_musculares:
            if campo in self.fields:
                self.fields[campo].widget.attrs['class'] = 'form-control'
                self.fields[campo].required = False
    
    def clean_nivel_dolor_inicial(self):
        value = self.cleaned_data.get('nivel_dolor_inicial')
        if value is None or value == '':
            return 0
        return value


# expedientes/forms.py - Actualiza ConsultaSegumientoForm

class ConsultaSegumientoForm(forms.ModelForm):
    """Formulario para Consulta de Seguimiento"""
    
    class Meta:
        model = ConsultaSegumiento
        exclude = ['created_at', 'updated_at', 'cita', 'profesional', 'expediente', 'numero_sesion', 'fecha_consulta'    ]
        widgets = {
            # Campos de texto
            'evolucion_paciente': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'respuesta_tratamiento': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'tecnicas_aplicadas': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'ejercicios_realizados': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'tratamiento_realizado': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'reevaluacion_rango_movimiento': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'plan_proxima_sesion': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'observaciones': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'localizacion_dolor': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            
            # Campos numéricos
            'nivel_dolor_actual': forms.HiddenInput(),
            'duracion_sesion': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            
            # Archivo
            'imagen_evolucion': forms.FileInput(attrs={'class': 'form-control-file'}),
            
            # Campos musculares
            'ms_eval1_izquierda': forms.Select(attrs={'class': 'form-control'}),
            'ms_eval1_derecha': forms.Select(attrs={'class': 'form-control'}),
            'mi_eval1_izquierda': forms.Select(attrs={'class': 'form-control'}),
            'mi_eval1_derecha': forms.Select(attrs={'class': 'form-control'}),
            'tronco_eval1_izquierda': forms.Select(attrs={'class': 'form-control'}),
            'tronco_eval1_derecha': forms.Select(attrs={'class': 'form-control'}),
            'cuello_eval1_izquierda': forms.Select(attrs={'class': 'form-control'}),
            'cuello_eval1_derecha': forms.Select(attrs={'class': 'form-control'}),
            
            # Campos goniométricos
            'ms_flexion_eval1_izq': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '°'}),
            'ms_flexion_eval1_der': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '°'}),
            'ms_extension_eval1_izq': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '°'}),
            'ms_extension_eval1_der': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '°'}),
            'ms_abduccion_eval1_izq': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '°'}),
            'ms_abduccion_eval1_der': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '°'}),
            'mi_flexion_eval1_izq': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '°'}),
            'mi_flexion_eval1_der': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '°'}),
            'mi_extension_eval1_izq': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '°'}),
            'mi_extension_eval1_der': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '°'}),
            'tronco_flexion_eval1': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '°'}),
            'tronco_extension_eval1': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '°'}),
            'tronco_lateral_izq_eval1': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '°'}),
            'tronco_lateral_der_eval1': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '°'}),
            'cuello_flexion_eval1': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '°'}),
            'cuello_extension_eval1': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '°'}),
            'cuello_lateral_izq_eval1': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '°'}),
            'cuello_lateral_der_eval1': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '°'}),
            'cuello_rotacion_izq_eval1': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '°'}),
            'cuello_rotacion_der_eval1': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '°'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Hacer que nivel_dolor_actual sea opcional (usamos slider)
        self.fields['nivel_dolor_actual'].required = False
        self.fields['nivel_dolor_actual'].widget = forms.HiddenInput()
        
        # Hacer campos obligatorios
        self.fields['evolucion_paciente'].required = True
        self.fields['tecnicas_aplicadas'].required = True
        
        # Campos opcionales
        self.fields['duracion_sesion'].required = False
        self.fields['respuesta_tratamiento'].required = False
        self.fields['ejercicios_realizados'].required = False
        self.fields['tratamiento_realizado'].required = False
        self.fields['reevaluacion_rango_movimiento'].required = False
        self.fields['plan_proxima_sesion'].required = False
        self.fields['observaciones'].required = False
        self.fields['localizacion_dolor'].required = False
    
    def clean_nivel_dolor_actual(self):
        value = self.cleaned_data.get('nivel_dolor_actual')
        if value is None or value == '':
            return 0
        return int(value) if value else 0

# expedientes/forms.py - Actualiza ConsultaFinalizacionForm
class ConsultaFinalizacionForm(forms.ModelForm):
    """Formulario para Consulta de Finalización"""
    
    # Definir explícitamente el campo para asegurar que es un IntegerField
    nivel_dolor_final = forms.IntegerField(
        required=False,
        initial=0,
        widget=forms.HiddenInput(),
        label='Nivel de dolor final'
    )
    
    class Meta:
        model = ConsultaFinalizacion
        exclude = ['created_at', 'updated_at', 'cita', 'profesional', 'expediente','fecha_consulta']
        widgets = {
            # Campos de texto
            'descripcion_tratamiento': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'objetivos_alcanzados': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'recomendaciones_finales': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'observaciones': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'localizacion_dolor': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            
            # Campos select
            'motivos_finalizacion': forms.Select(attrs={'class': 'form-control select2'}),
            
            # Campos musculares y goniométricos (opcionales)
            'ms_eval1_izquierda': forms.Select(attrs={'class': 'form-control'}),
            'ms_eval1_derecha': forms.Select(attrs={'class': 'form-control'}),
            'mi_eval1_izquierda': forms.Select(attrs={'class': 'form-control'}),
            'mi_eval1_derecha': forms.Select(attrs={'class': 'form-control'}),
            'tronco_eval1_izquierda': forms.Select(attrs={'class': 'form-control'}),
            'tronco_eval1_derecha': forms.Select(attrs={'class': 'form-control'}),
            'cuello_eval1_izquierda': forms.Select(attrs={'class': 'form-control'}),
            'cuello_eval1_derecha': forms.Select(attrs={'class': 'form-control'}),
            
            # Campos goniométricos
            'ms_flexion_eval1_izq': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '°'}),
            'ms_flexion_eval1_der': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '°'}),
            'ms_extension_eval1_izq': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '°'}),
            'ms_extension_eval1_der': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '°'}),
            'ms_abduccion_eval1_izq': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '°'}),
            'ms_abduccion_eval1_der': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '°'}),
            'mi_flexion_eval1_izq': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '°'}),
            'mi_flexion_eval1_der': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '°'}),
            'mi_extension_eval1_izq': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '°'}),
            'mi_extension_eval1_der': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '°'}),
            'tronco_flexion_eval1': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '°'}),
            'tronco_extension_eval1': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '°'}),
            'tronco_lateral_izq_eval1': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '°'}),
            'tronco_lateral_der_eval1': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '°'}),
            'cuello_flexion_eval1': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '°'}),
            'cuello_extension_eval1': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '°'}),
            'cuello_lateral_izq_eval1': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '°'}),
            'cuello_lateral_der_eval1': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '°'}),
            'cuello_rotacion_izq_eval1': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '°'}),
            'cuello_rotacion_der_eval1': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '°'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Hacer campos obligatorios
        self.fields['motivos_finalizacion'].required = True
        self.fields['objetivos_alcanzados'].required = True
        
        # Campos opcionales
        self.fields['descripcion_tratamiento'].required = False
        self.fields['recomendaciones_finales'].required = False
        self.fields['observaciones'].required = False
        self.fields['localizacion_dolor'].required = False
        self.fields['nivel_dolor_final'].required = False
    
    def clean_nivel_dolor_final(self):
        value = self.cleaned_data.get('nivel_dolor_final')
        if value is None or value == '':
            return 0
        try:
            return int(value)
        except (ValueError, TypeError):
            return 0