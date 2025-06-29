from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Notificacion

@login_required
def ver_notificaciones(request):
    # Marcar todas como leídas al abrir la página
    request.user.notificaciones.filter(leida=False).update(leida=True)
    
    notificaciones = request.user.notificaciones.all()
    
    return render(request, 'notifications/lista_notificaciones.html', {
        'notificaciones': notificaciones,
        'titulo': 'Todas mis notificaciones'
    })

@login_required
def marcar_como_leida(request, pk):
    notificacion = request.user.notificaciones.get(pk=pk)
    notificacion.marcar_como_leida()
    return redirect(notificacion.get_absolute_url())