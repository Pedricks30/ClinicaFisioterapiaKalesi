from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from users.models import CustomUser

class CustomAuthenticationForm(AuthenticationForm):
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not CustomUser.objects.filter(username=username).exists():
            raise ValidationError("No existe un usuario con este nombre.")
        return username

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if user is None:
                raise ValidationError("Contraseña incorrecta.")
        return cleaned_data