# expedientes/widgets.py
from django import forms
from django.utils.safestring import mark_safe

class SiNoEspecificacionWidget(forms.Widget):
    """Widget que muestra un selector Sí/No y un campo de especificación"""
    
    template_name = 'widgets/si_no_especificacion.html'
    
    def __init__(self, attrs=None, etiqueta_si_no="¿Presenta?", placeholder="Especifique..."):
        self.etiqueta_si_no = etiqueta_si_no
        self.placeholder = placeholder
        super().__init__(attrs)
    
    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        
        # Separar el valor combinado en partes
        estado = 'no'
        especificacion = ''
        
        if value:
            value_str = str(value)
            if value_str.startswith('SÍ:'):
                estado = 'si'
                especificacion = value_str[3:].strip()
                if especificacion == '(sin especificar)':
                    especificacion = ''
            elif value_str.startswith('NO:'):
                estado = 'no'
                especificacion = value_str[3:].strip()
        
        context['widget'].update({
            'estado': estado,
            'especificacion': especificacion,
            'etiqueta_si_no': self.etiqueta_si_no,
            'placeholder': self.placeholder,
            'name_si_no': f'{name}_si_no',
            'name_especificacion': f'{name}_especificacion',
        })
        return context
    
    def value_from_datadict(self, data, files, name):
        """Recupera el valor combinado de los datos del formulario"""
        si_no = data.get(f'{name}_si_no')
        especificacion = data.get(f'{name}_especificacion', '')
        
        if si_no == 'si':
            if especificacion:
                return f"SÍ: {especificacion.strip()}"
            return "SÍ: (sin especificar)"
        elif si_no == 'no':
            if especificacion:
                return f"NO: {especificacion.strip()}"
            return "NO"
        return ""
    
    def render(self, name, value, attrs=None, renderer=None):
        """Render manual para compatibilidad"""
        context = self.get_context(name, value, attrs)
        html = f'''
        <div class="si-no-especificacion-widget">
            <div class="row">
                <div class="col-auto">
                    <label class="form-label fw-bold">{context['widget']['etiqueta_si_no']}</label>
                    <div class="d-flex gap-3">
                        <div class="form-check">
                            <input type="radio" 
                                   name="{context['widget']['name_si_no']}" 
                                   value="si" 
                                   id="{name}_si"
                                   class="form-check-input"
                                   {'checked' if context['widget']['estado'] == 'si' else ''}>
                            <label class="form-check-label" for="{name}_si">Sí</label>
                        </div>
                        <div class="form-check">
                            <input type="radio" 
                                   name="{context['widget']['name_si_no']}" 
                                   value="no" 
                                   id="{name}_no"
                                   class="form-check-input"
                                   {'checked' if context['widget']['estado'] == 'no' else ''}>
                            <label class="form-check-label" for="{name}_no">No</label>
                        </div>
                    </div>
                </div>
                <div class="col">
                    <input type="text" 
                           name="{context['widget']['name_especificacion']}" 
                           id="{name}_especificacion"
                           class="form-control"
                           placeholder="{context['widget']['placeholder']}"
                           value="{context['widget']['especificacion']}"
                           {'disabled' if context['widget']['estado'] == 'no' else ''}>
                </div>
            </div>
        </div>
        <script>
            (function() {{
                var radioSi = document.getElementById('{name}_si');
                var radioNo = document.getElementById('{name}_no');
                var inputEspecificacion = document.getElementById('{name}_especificacion');
                
                function actualizarEstadoEspecificacion() {{
                    if (radioSi && radioSi.checked) {{
                        inputEspecificacion.disabled = false;
                    }} else if (radioNo && radioNo.checked) {{
                        inputEspecificacion.disabled = true;
                        inputEspecificacion.value = '';
                    }}
                }}
                
                if (radioSi && radioNo && inputEspecificacion) {{
                    radioSi.addEventListener('change', actualizarEstadoEspecificacion);
                    radioNo.addEventListener('change', actualizarEstadoEspecificacion);
                    actualizarEstadoEspecificacion();
                }}
            }})();
        </script>
        '''
        return mark_safe(html)