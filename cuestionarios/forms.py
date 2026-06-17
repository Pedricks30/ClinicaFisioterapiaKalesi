# cuestionarios/forms.py
from django import forms
from .models import Cuestionario, PreguntaCuestionario

class CuestionarioForm(forms.ModelForm):
    class Meta:
        model = Cuestionario
        fields = ['nombre', 'descripcion', 'tipo_cuestionario', 'activo']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Evaluación de Hombro'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Describa el propósito del cuestionario...'
            }),
            'tipo_cuestionario': forms.Select(attrs={
                'class': 'form-select'
            }),
            'activo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }

class PreguntaCuestionarioForm(forms.ModelForm):
    class Meta:
        model = PreguntaCuestionario
        fields = [
            'texto_pregunta', 'tipo_pregunta', 'orden', 'obligatorio',
            'opciones', 'escala_min', 'escala_max', 'etiqueta_min', 
            'etiqueta_max', 'es_indicador_clave', 'umbral_alarma'
        ]
        widgets = {
            'texto_pregunta': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Escriba la pregunta aquí...'
            }),
            'tipo_pregunta': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_tipo_pregunta'
            }),
            'orden': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0
            }),
            'obligatorio': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'opciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Opción 1\nOpción 2\nOpción 3\n(Una por línea)'
            }),
            'escala_min': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0
            }),
            'escala_max': forms.NumberInput(attrs={
                'class': 'form-control',
                'max': 10
            }),
            'etiqueta_min': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Sin dolor'
            }),
            'etiqueta_max': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Máximo dolor'
            }),
            'es_indicador_clave': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'umbral_alarma': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'max': 10,
                'placeholder': 'Ej: 7'
            })
        }
    
    def clean_opciones(self):
        opciones = self.cleaned_data.get('opciones')
        if self.cleaned_data.get('tipo_pregunta') == 'MULTIPLE' and opciones:
            # Convertir texto a lista
            opciones_list = [opt.strip() for opt in opciones.split('\n') if opt.strip()]
            return opciones_list
        return None
    
    def clean(self):
        cleaned_data = super().clean()
        tipo = cleaned_data.get('tipo_pregunta')
        
        if tipo in ['ESCALA', 'ESCALA_NUMERICA']:
            min_val = cleaned_data.get('escala_min', 0)
            max_val = cleaned_data.get('escala_max', 10)
            if min_val >= max_val:
                self.add_error('escala_max', 'El valor máximo debe ser mayor al mínimo')
        
        return cleaned_data

class RespuestaCuestionarioFormSet(forms.Form):
    """Formset dinámico para respuestas"""
    
    def __init__(self, *args, preguntas=None, **kwargs):
        super().__init__(*args, **kwargs)
        if preguntas:
            for pregunta in preguntas:
                field_name = f'pregunta_{pregunta.id}'
                
                if pregunta.tipo_pregunta in ['ESCALA', 'ESCALA_NUMERICA']:
                    self.fields[field_name] = forms.ChoiceField(
                        choices=[(i, str(i)) for i in range(pregunta.escala_min, pregunta.escala_max + 1)],
                        widget=forms.RadioSelect(attrs={'class': 'escala-radio'}),
                        required=pregunta.obligatorio,
                        label=pregunta.texto_pregunta
                    )
                
                elif pregunta.tipo_pregunta == 'TEXTO':
                    self.fields[field_name] = forms.CharField(
                        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
                        required=pregunta.obligatorio,
                        label=pregunta.texto_pregunta
                    )
                
                elif pregunta.tipo_pregunta == 'SI_NO':
                    self.fields[field_name] = forms.ChoiceField(
                        choices=[('si', 'Sí'), ('no', 'No')],
                        widget=forms.RadioSelect(attrs={'class': 'si-no-radio'}),
                        required=pregunta.obligatorio,
                        label=pregunta.texto_pregunta
                    )
                
                elif pregunta.tipo_pregunta == 'MULTIPLE':
                    choices = [(opt, opt) for opt in pregunta.opciones] if pregunta.opciones else []
                    self.fields[field_name] = forms.ChoiceField(
                        choices=choices,
                        widget=forms.Select(attrs={'class': 'form-select'}),
                        required=pregunta.obligatorio,
                        label=pregunta.texto_pregunta
                    )