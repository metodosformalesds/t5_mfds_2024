# forms.py
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms

class CreateUserForm(UserCreationForm):
    USER_TYPE_CHOICES = [
        ('viajero', 'Viajero'),
        ('agencia', 'Agencia'),
    ]

    user_type = forms.ChoiceField(choices=USER_TYPE_CHOICES, label="Tipo de usuario")

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'user_type']
        labels = {
            'username': "Nombre de usuario",
            'email': "Correo electrónico",
            'password1': "Contraseña",
            'password2': 'Confirmar contraseña',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].label = 'Contraseña'
        self.fields['password2'].label = 'Confirmar contraseña'
