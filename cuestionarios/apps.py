# cuestionarios/apps.py
from django.apps import AppConfig

class CuestionariosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'cuestionarios'
    verbose_name = 'Gestión de Cuestionarios Dinámicos'
    
    def ready(self):
        import cuestionarios.signals