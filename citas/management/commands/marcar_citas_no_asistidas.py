# citas/management/commands/marcar_citas_no_asistidas.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q
from citas.models import Cita, CitaHistorico
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Marca automáticamente como "No Asistió" las citas que ya pasaron y no fueron completadas'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=1,
            help='Número de días de gracia después de la fecha de la cita (default: 1)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simula la ejecución sin hacer cambios'
        )

    def handle(self, *args, **options):
        days_grace = options.get('days', 1)
        dry_run = options.get('dry_run', False)
        
        self.stdout.write(self.style.SUCCESS(f'=== MARCANDO CITAS NO ASISTIDAS ==='))
        self.stdout.write(f'Días de gracia: {days_grace}')
        self.stdout.write(f'Modo simulación: {"SÍ" if dry_run else "NO"}')
        self.stdout.write('-' * 50)
        
        ahora = timezone.now()
        fecha_limite = ahora - timedelta(days=days_grace)
        
        # Buscar citas que:
        # 1. Tienen fecha anterior a la fecha límite
        # 2. Están en estado PENDIENTE o CONFIRMADA
        # 3. No están canceladas
        citas_a_marcar = Cita.objects.filter(
            fecha__lt=fecha_limite,
            estado__in=['PENDIENTE', 'CONFIRMADA']
        ).select_related('paciente', 'profesional')
        
        count = citas_a_marcar.count()
        
        if count == 0:
            self.stdout.write(self.style.WARNING('No hay citas para marcar como no asistidas'))
            return
        
        self.stdout.write(f'Se encontraron {count} citas para marcar como no asistidas')
        
        if dry_run:
            self.stdout.write('\n📋 CITAS QUE SE MARCARÍAN (SIMULACIÓN):')
            for cita in citas_a_marcar:
                self.stdout.write(
                    f'  • Cita #{cita.id} - {cita.paciente.get_full_name()} - '
                    f'{cita.fecha.strftime("%d/%m/%Y %H:%M")} - '
                    f'{cita.get_tipo_cita_display()}'
                )
            self.stdout.write(self.style.WARNING('\n🔍 Modo simulación - No se realizaron cambios'))
            return
        
        # Contadores
        marcadas = 0
        errores = 0
        
        for cita in citas_a_marcar:
            try:
                # Obtener usuario del sistema para el registro
                sistema_user, created = User.objects.get_or_create(
                    username='sistema_citas',
                    defaults={
                        'email': 'sistema@clinica.com',
                        'first_name': 'Sistema',
                        'last_name': 'Citas',
                        'tipo_usuario': 'ADMIN',
                        'is_active': True
                    }
                )
                
                # Cambiar estado
                cita.estado = 'NO_ASISTIO'
                cita.save(update_fields=['estado'])
                
                # Registrar en el histórico
                CitaHistorico.objects.create(
                    cita_original=cita,
                    fecha_original=cita.fecha,
                    fecha_cambio=timezone.now(),
                    motivo=f"Marcado automático por sistema - Cita no asistida (venció el {cita.fecha.strftime('%d/%m/%Y %H:%M')})",
                    usuario=sistema_user,
                    tipo_cambio='NO_ASISTIO'
                )
                
                # Enviar notificación al paciente
                try:
                    cita.enviar_notificacion('no_asistio')
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f'  ⚠️ Error al enviar notificación para cita #{cita.id}: {str(e)}'))
                
                marcadas += 1
                self.stdout.write(self.style.SUCCESS(f'  ✅ Cita #{cita.id} marcada como NO ASISTIÓ'))
                
            except Exception as e:
                errores += 1
                self.stdout.write(self.style.ERROR(f'  ❌ Error al procesar cita #{cita.id}: {str(e)}'))
        
        # Resumen final
        self.stdout.write('-' * 50)
        self.stdout.write(self.style.SUCCESS(f'✅ RESUMEN FINAL:'))
        self.stdout.write(f'  • Procesadas: {count}')
        self.stdout.write(f'  • Marcadas: {marcadas}')
        self.stdout.write(f'  • Errores: {errores}')