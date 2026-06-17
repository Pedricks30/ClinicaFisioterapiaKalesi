# citas/admin.py
from django.contrib import admin
from django.urls import path
from django.shortcuts import redirect
from django.contrib import messages
from django.core.management import call_command
from .models import Cita, CitaHistorico

@admin.register(Cita)
class CitaAdmin(admin.ModelAdmin):
    list_display = ['id', 'paciente', 'profesional', 'fecha', 'estado', 'tipo_cita']
    list_filter = ['estado', 'tipo_cita', 'fecha']
    search_fields = ['paciente__nombres', 'paciente__apellidos', 'paciente__documento_identidad']
    date_hierarchy = 'fecha'
    readonly_fields = ['created_at', 'updated_at']
    
    actions = ['marcar_no_asistidas_action']
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('marcar-no-asistidas/', self.admin_site.admin_view(self.marcar_no_asistidas), name='marcar_no_asistidas'),
        ]
        return custom_urls + urls
    
    def marcar_no_asistidas(self, request):
        """Vista para ejecutar el comando desde el admin"""
        try:
            call_command('marcar_citas_no_asistidas', days=1)
            self.message_user(request, 'Citas no asistidas marcadas correctamente', level='success')
        except Exception as e:
            self.message_user(request, f'Error: {str(e)}', level='error')
        return redirect('admin:citas_cita_changelist')
    
    def marcar_no_asistidas_action(self, request, queryset):
        """Acción masiva para marcar citas seleccionadas como no asistidas"""
        count = 0
        for cita in queryset:
            if cita.estado in ['PENDIENTE', 'CONFIRMADA']:
                try:
                    cita.marcar_no_asistio(request.user)
                    count += 1
                except Exception as e:
                    self.message_user(request, f'Error en cita #{cita.id}: {str(e)}', level='error')
        
        self.message_user(request, f'{count} cita(s) marcadas como No Asistieron', level='success')
    
    marcar_no_asistidas_action.short_description = "Marcar citas seleccionadas como No Asistieron"

@admin.register(CitaHistorico)
class CitaHistoricoAdmin(admin.ModelAdmin):
    list_display = ['cita_original', 'tipo_cambio', 'fecha_cambio', 'usuario']
    list_filter = ['tipo_cambio']
    search_fields = ['cita_original__paciente__nombres', 'cita_original__paciente__apellidos']
    readonly_fields = ['created_at', 'update_at']