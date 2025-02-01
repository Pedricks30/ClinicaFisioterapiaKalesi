from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .forms import CustomUserCreationForm #Importar el formulario personalizado

# Create your views here.

def index(request):
    context = {
        'mensaje': 'Hola, este es un mensaje desde la vista.'
    }
    return render(request, 'cursos/index.html', context)

def registrar_usuario(request):
    if request.method == 'GET':
        # Mostrar el formulario de registro
        return render(request, 'user/registration.html', {
            'form': CustomUserCreationForm()  # Usa el formulario personalizado
        })
    else:
        # Procesar el formulario enviado
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            # Guardar el usuario con los datos del formulario
            user = form.save()
            return redirect('curso_crud')  # Redirigir después del registro
        else:
            # Mostrar el formulario con errores
            return render(request, 'user/registration.html', {
                'form': form
            })
