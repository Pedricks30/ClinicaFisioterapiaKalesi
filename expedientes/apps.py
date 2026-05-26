# expedientes/apps.py
from django.apps import AppConfig

class ExpedientesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'expedientes'

    def ready(self):
        import expedientes.signals  # Importa las señales para que se registren correctamente