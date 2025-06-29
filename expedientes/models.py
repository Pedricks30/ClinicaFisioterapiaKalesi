from django.db import models
from paciente.models import Patient

class Expediente(models.Model):
    paciente = models.OneToOneField(Patient, on_delete=models.CASCADE, related_name='expediente')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    notas_generales = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"Expediente de {self.paciente}"

class HistoriaClinica(models.Model):
    expediente = models.ForeignKey(Expediente, on_delete=models.CASCADE, related_name='historias')
    fecha = models.DateTimeField(auto_now_add=True)
    medico = models.ForeignKey('medical.MedicalUser', on_delete=models.SET_NULL, null=True)
    diagnostico = models.TextField()
    tratamiento = models.TextField()
    notas = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-fecha']
    
    def __str__(self):
        return f"Historia del {self.fecha.date()}"