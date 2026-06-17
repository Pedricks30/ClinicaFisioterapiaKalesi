# citas/scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
from django.core.management import call_command
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

def marcar_citas_no_asistidas_job():
    """Ejecuta el comando para marcar citas no asistidas"""
    try:
        logger.info(f"[{timezone.now()}] Iniciando marcado automático de citas no asistidas")
        call_command('marcar_citas_no_asistidas', days=1)
        logger.info(f"[{timezone.now()}] ✅ Completado: marcado de citas no asistidas")
    except Exception as e:
        logger.error(f"[{timezone.now()}] ❌ Error en marcado automático: {str(e)}")

_scheduler = None

def start_scheduler():
    """Inicia el scheduler con el job para marcar citas no asistidas"""
    global _scheduler
    
    if _scheduler is not None:
        return _scheduler
    
    try:
        scheduler = BackgroundScheduler()
        
        # ✅ NO usar DjangoJobStore para evitar accesos a la BD
        scheduler.add_job(
            marcar_citas_no_asistidas_job,
            'interval',
            minutes=1,
            id='marcar_citas_no_asistidas'
        )
        
        scheduler.start()
        _scheduler = scheduler
        logger.info("✅ Scheduler iniciado correctamente")
        return scheduler
        
    except Exception as e:
        logger.error(f"❌ Error iniciando scheduler: {str(e)}")
        return None

def get_scheduler():
    if _scheduler is None:
        return start_scheduler()
    return _scheduler