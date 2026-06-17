# expedientes/signals.py
from django.db.models.signals import post_save, pre_delete, post_delete
from django.dispatch import receiver
from django.db import transaction
from .models import Expediente  # Importación lazy


# =============================================================================
# SEÑAL PARA CREAR EL EXPEDIENTE AL CREAR EL PACIENTE
# =============================================================================
@receiver(post_save, sender='paciente.Patient')
def crear_expediente_paciente(sender, instance, created, **kwargs):
    """Crea automáticamente un expediente cuando se registra un nuevo paciente"""
    if created:
        nombre_completo = f"{instance.nombres} {instance.apellidos}"
        Expediente.objects.create(
            paciente=instance,
            notas_generales=f"Expediente de fisioterapia creado para {nombre_completo}. Pendiente de primera consulta."
        )

# =============================================================================
# SEÑAL PARA ELIMINAR EXPEDIENTE AL ELIMINAR PACIENTE (RESPALDO)
# =============================================================================
@receiver(pre_delete, sender='paciente.Patient')
def eliminar_expediente_automatico(sender, instance, **kwargs):
    """Elimina automáticamente el expediente al borrar un paciente"""
    try:
        if hasattr(instance, 'expediente'):
            expediente = instance.expediente
            print(f"Eliminando expediente {expediente.numero_expediente} del paciente {instance.nombres} {instance.apellidos}")
            expediente.delete()
    except Expediente.DoesNotExist:
        print(f"El paciente {instance.nombres} {instance.apellidos} no tenía expediente asociado")
    except Exception as e:
        print(f"Error al eliminar expediente del paciente {instance.id}: {str(e)}")


# =============================================================================
# SEÑALES PARA LIMPIAR REFERENCIAS DE CITAS (CORREGIDAS)
# =============================================================================
@receiver(pre_delete, sender='expedientes.PrimeraConsulta')
def limpiar_referencia_cita_primera(sender, instance, **kwargs):
    """Limpia la referencia en la cita antes de eliminar una primera consulta"""
    try:
        if instance.cita:
            instance.cita.primera_consulta = None
            instance.cita.save(update_fields=['primera_consulta'])
            print(f"✅ Referencia de cita {instance.cita.id} limpiada correctamente")
    except Exception as e:
        print(f"❌ Error al limpiar referencia de cita: {str(e)}")


@receiver(pre_delete, sender='expedientes.ConsultaSegumiento')
def limpiar_referencia_cita_seguimiento(sender, instance, **kwargs):
    """Limpia la referencia en la cita antes de eliminar un seguimiento"""
    try:
        if instance.cita:
            instance.cita.seguimiento = None
            instance.cita.save(update_fields=['seguimiento'])
            print(f"✅ Referencia de cita {instance.cita.id} limpiada correctamente")
    except Exception as e:
        print(f"❌ Error al limpiar referencia de cita: {str(e)}")


@receiver(pre_delete, sender='expedientes.ConsultaFinalizacion')
def limpiar_referencia_cita_finalizacion(sender, instance, **kwargs):
    """Limpia la referencia en la cita antes de eliminar una finalización"""
    try:
        if instance.cita:
            instance.cita.finalizacion = None
            instance.cita.save(update_fields=['finalizacion'])
            print(f"✅ Referencia de cita {instance.cita.id} limpiada correctamente")
    except Exception as e:
        print(f"❌ Error al limpiar referencia de cita: {str(e)}")


# =============================================================================
# SEÑAL PARA LIMPIAR TODAS LAS REFERENCIAS DE CITAS AL ELIMINAR EXPEDIENTE
# =============================================================================
@receiver(pre_delete, sender='expedientes.Expediente')
def limpiar_todas_referencias_citas(sender, instance, **kwargs):
    """Limpia todas las referencias en citas antes de eliminar un expediente"""
    try:
        if hasattr(instance, 'primera_consulta') and instance.primera_consulta:
            if instance.primera_consulta.cita:
                instance.primera_consulta.cita.primera_consulta = None
                instance.primera_consulta.cita.save(update_fields=['primera_consulta'])
        
        for seguimiento in instance.seguimientos.all():
            if seguimiento.cita:
                seguimiento.cita.seguimiento = None
                seguimiento.cita.save(update_fields=['seguimiento'])
        
        if hasattr(instance, 'finalizacion') and instance.finalizacion:
            if instance.finalizacion.cita:
                instance.finalizacion.cita.finalizacion = None
                instance.finalizacion.cita.save(update_fields=['finalizacion'])
        print(f"✅ Todas las referencias de citas del expediente {instance.numero_expediente} limpiadas correctamente")
    except Exception as e:
        print(f"❌ Error al limpiar referencias de citas: {str(e)}")


# =============================================================================
# SEÑALES PARA LOGGING
# =============================================================================
@receiver(post_delete, sender='paciente.Patient')
def verificar_limpieza_despues_eliminar_paciente(sender, instance, **kwargs):
    """Verifica la limpieza después de eliminar un paciente"""
    print(f"✓ Paciente {instance.nombres} {instance.apellidos} (ID: {instance.id}) eliminado correctamente")


@receiver(pre_delete, sender='expedientes.ConsultaFinalizacion')
def log_eliminar_finalizacion(sender, instance, **kwargs):
    """Log cuando se elimina una finalización"""
    try:
        cantidad_ejercicios = instance.ejercicios_detallados.count() if hasattr(instance, 'ejercicios_detallados') else 0
        if cantidad_ejercicios > 0:
            print(f"Eliminando finalización con {cantidad_ejercicios} ejercicios asociados del paciente {instance.expediente.paciente}")
    except Exception as e:
        print(f"Error al loggear eliminación: {str(e)}")


# =============================================================================
# SEÑAL PARA ACTUALIZAR EL ESTADO DEL EXPEDIENTE BASADO EN CITAS
# =============================================================================
@receiver(post_save, sender='citas.Cita')
def actualizar_estado_expediente_por_cita(sender, instance, created, **kwargs):
    """Actualiza el estado del expediente basado en las citas completadas"""
    from .models import Expediente  # Importación lazy
    try:
        if not instance.paciente:
            return
            
        try:
            expediente = instance.paciente.expediente
        except Expediente.DoesNotExist:
            print(f"⚠ Advertencia: El paciente {instance.paciente.id} no tiene expediente asociado")
            return
        
        if instance.tipo_cita == 'PRIMERA_CONSULTA' and instance.estado == 'COMPLETADA':
            if expediente.estado not in ['ACTIVO']:
                expediente.estado = 'ACTIVO'
                expediente.fecha_inicio_tratamiento = expediente.fecha_inicio_tratamiento or instance.fecha.date()
                expediente.save(update_fields=['estado', 'fecha_inicio_tratamiento'])
                print(f"✓ Expediente {expediente.numero_expediente} marcado como ACTIVO")
        
        elif instance.tipo_cita == 'FINALIZACION' and instance.estado == 'COMPLETADA':
            expediente.estado = 'FINALIZADO'
            expediente.fecha_fin_tratamiento = instance.fecha.date()
            expediente.save(update_fields=['estado', 'fecha_fin_tratamiento'])
            print(f"✓ Expediente {expediente.numero_expediente} marcado como FINALIZADO")
                
    except Exception as e:
        print(f"❌ Error al actualizar estado del expediente: {str(e)}")