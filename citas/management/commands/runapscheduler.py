# citas/management/commands/runapscheduler.py
from django.core.management.base import BaseCommand
from apscheduler.schedulers.background import BackgroundScheduler
from django.core.management import call_command
from django.utils import timezone
import logging
import time

logger = logging.getLogger(__name__)

# ✅ Función a nivel de módulo
def marcar_citas_job():
    """Ejecuta el comando para marcar citas no asistidas"""
    try:
        print(f"[{timezone.now()}] 📋 Marcando citas no asistidas...")
        call_command('marcar_citas_no_asistidas', days=1)
        print(f"[{timezone.now()}] ✅ Completado exitosamente")
    except Exception as e:
        print(f"[{timezone.now()}] ❌ Error: {str(e)}")

class Command(BaseCommand):
    help = 'Ejecuta el scheduler de APScheduler para marcar citas no asistidas'
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🚀 Iniciando scheduler de citas...'))
        
        # ✅ Crear scheduler sin DjangoJobStore
        scheduler = BackgroundScheduler()
        
        # ✅ Agregar el job
        scheduler.add_job(
            marcar_citas_job,
            'interval',
            minutes=1400,  # Para pruebas (cada 1 minuto)
            id='marcar_citas_no_asistidas'
        )
        
        # ✅ Iniciar
        scheduler.start()
        self.stdout.write(self.style.SUCCESS('✅ Scheduler ejecutándose. Presiona Ctrl+C para detener.'))
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING('⏹️ Deteniendo scheduler...'))
            scheduler.shutdown()
            self.stdout.write(self.style.SUCCESS('✅ Scheduler detenido correctamente'))