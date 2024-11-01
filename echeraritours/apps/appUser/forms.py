# forms.py
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from django.core.exceptions import ValidationError


class CreateUserForm(UserCreationForm):
    """
    A form for creating new users. Inherits from Django's UserCreationForm.
    Attributes:
        Meta:
            model (User): The model that will be used for creating the user.
            fields (list): The fields that will be included in the form.
            labels (dict): Custom labels for the form fields.
    Methods:
        __init__(self, *args, **kwargs):
            Initializes the form and sets custom labels for password fields.
        clean_email(self):
            Validates that the provided email is unique.
            Raises:
                ValidationError: If the email is already registered.
            Returns:
                str: The cleaned email.
    """
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
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

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError(
                "Este correo electrónico ya está registrado.")
        return email
