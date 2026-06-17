# citas/management/commands/actualizar_tipos_citas.py
from django.core.management.base import BaseCommand
from citas.models import Cita
from django.db import transaction

class Command(BaseCommand):
    help = 'Actualiza los tipos de cita para citas existentes que no tienen tipo'

    def handle(self, *args, **options):
        # Buscar citas sin tipo_cita
        citas_sin_tipo = Cita.objects.filter(tipo_cita__isnull=True)
        count = citas_sin_tipo.count()
        
        self.stdout.write(f"Encontradas {count} citas sin tipo")
        
        if count == 0:
            self.stdout.write(self.style.SUCCESS("No hay citas sin tipo para actualizar"))
            return
        
        with transaction.atomic():
            for cita in citas_sin_tipo:
                try:
                    # Determinar tipo basado en el historial del paciente
                    citas_completadas = Cita.objects.filter(
                        paciente=cita.paciente,
                        profesional=cita.profesional,
                        estado='COMPLETADA'
                    ).exclude(pk=cita.pk)
                    
                    tiene_primera = citas_completadas.filter(
                        tipo_cita='PRIMERA_CONSULTA'
                    ).exists()
                    
                    tiene_finalizacion = citas_completadas.filter(
                        tipo_cita='FINALIZACION'
                    ).exists()
                    
                    if tiene_finalizacion:
                        cita.tipo_cita = 'REVISION'
                    elif not tiene_primera:
                        cita.tipo_cita = 'PRIMERA_CONSULTA'
                    else:
                        cita.tipo_cita = 'SEGUIMIENTO'
                    
                    cita.save(update_fields=['tipo_cita'])
                    self.stdout.write(f"✅ Cita #{cita.id}: {cita.tipo_cita}")
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"❌ Error en cita #{cita.id}: {str(e)}"))
        
        self.stdout.write(self.style.SUCCESS(f"✅ Proceso completado. Actualizadas {Cita.objects.filter(tipo_cita__isnull=True).count()} citas"))