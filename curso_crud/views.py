from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm #Importar el formulario personalizado
from django.contrib.auth import authenticate, login as auth_login
from django.contrib import messages
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
        # Procesar el formulario enviado (incluyendo archivos)
        form = CustomUserCreationForm(request.POST, request.FILES)  # ¡Aquí agregamos request.FILES!
        if form.is_valid():
            # Guardar el usuario con los datos del formulario
            user = form.save()
            return redirect('curso_crud')  # Redirigir después del registro
        else:
            # Mostrar el formulario con errores
            return render(request, 'user/registration.html', {
                'form': form
            })
        
def login(request):
    if request.method == 'POST':
        email = request.POST.get('email', '')  # Devuelve '' si 'email' no existe
        password = request.POST.get('password', '')  # Devuelve '' si 'password' no existe

        user = authenticate(request, username=email, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect('curso_crud')
        else:
            messages.error(request, 'Credenciales inválidas')
            messages.error(request, 'Debes ingresar tu correo y contraseña')
    return render(request, 'registration/login.html')

def forgot_password(request):
    return render(request, 'registration/forgot_password.html')