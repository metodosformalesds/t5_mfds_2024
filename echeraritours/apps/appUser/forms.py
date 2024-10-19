from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms


class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        labels = {
            'username': "Nombre de usuario",
            'email': "Correo electronico",
            'password1': "Contraseña",
            'password2': 'Confirmar contraseña',
        }

    def __init__(self, *args, **kwargs):
        """Cambia los parametros de los labels para que salgan en español
        """
        super().__init__(*args, **kwargs)
        self.fields['password1'].label = 'Contraseña'
        self.fields['password2'].label = 'Confirmar contraseña'
