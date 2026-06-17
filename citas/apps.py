# citas/apps.py
import logging
from django.apps import AppConfig

logger = logging.getLogger(__name__)

class CitasConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'citas'
    scheduler_started = False
    
    def ready(self):
        """Iniciar el scheduler cuando Django esté listo"""
        import sys
        import os
        
        # ✅ Solo iniciar en el proceso principal (no en recarga de archivos)
        if os.environ.get('RUN_MAIN') != 'true':
            return
            
        if 'runserver' in sys.argv or 'runapscheduler' in sys.argv:
            if not self.scheduler_started:
                try:
                    from .scheduler import get_scheduler
                    scheduler = get_scheduler()
                    self.scheduler_started = True
                    logger.info("✅ Scheduler de citas iniciado correctamente")
                except Exception as e:
                    logger.error(f"❌ Error iniciando scheduler: {str(e)}")