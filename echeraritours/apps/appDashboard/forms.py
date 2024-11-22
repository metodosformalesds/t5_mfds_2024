from django import forms
from django.core.exceptions import ValidationError
from apps.appUser.models import Client, Agency
from apps.appTour.models import Reviews
from datetime import date


class UserForm(forms.ModelForm):
    """
    Author: Santiago Mendivil
    A form for creating and updating Client instances.
    Fields:
        first_name (str): The first name of the client.
        maternal_surname (str): The maternal surname of the client.
        paternal_surname (str): The paternal surname of the client.
        city (str): The city where the client resides.
        phone (str): The phone number of the client.
        birth_date (date): The birth date of the client.
        zip_code (str): The zip code of the client's address.
        profile_image (ImageField): The profile image of the client.
    Methods:
        __init__(*args, **kwargs): Initializes the form and adds 'form-control' class to each field's widget.
        clean_phone(): Validates the phone number to ensure it has between 9 and 15 digits.
        clean_birth_date(): Validates the birth date to ensure the client is at least 18 years old.
    """
    class Meta:
        model = Client
        fields = ['first_name', 'maternal_surname', 'paternal_surname', 'city',
                  'phone', 'birth_date', 'zip_code', 'profile_image']

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if len(phone) < 9:
            raise ValidationError(
                'El número de teléfono debe tener al menos 9 dígitos.')

        if len(phone) > 10:
            raise ValidationError(
                'El número de teléfono debe tener máximo 15 dígitos.')
        return phone

    def clean_birth_date(self):
        birth_date = self.cleaned_data.get('birth_date')
        today = date.today()
        age = today.year - birth_date.year - \
            ((today.month, today.day) < (birth_date.month, birth_date.day))

        if age < 18:
            raise ValidationError('Debes ser mayor de edad para registrarte.')

        return birth_date


class UserProfileForm(forms.ModelForm):
    """
    Author: Santiago Mendivil
    UserProfileForm is a Django ModelForm for the Client model, specifically for handling user profile updates.
    Attributes:
        profile_image (forms.ImageField): An optional image field for the user's profile picture. It uses a FileInput widget and provides a custom error message for invalid files.
    Meta:
        model (Client): The model associated with this form.
        fields (list): A list of fields to include in the form, in this case, only 'profile_image'.
    Methods:
        __init__(self, *args, **kwargs): Initializes the form and adds a 'form-control' CSS class to all fields.
        clean_phone(self): Validates the phone number to ensure it has at least 9 digits. Raises a ValidationError if the condition is not met.
        clean_birth_date(self): Validates the birth date to ensure the user is at least 18 years old. Raises a ValidationError if the condition is not met.
    """
    profile_image = forms.ImageField(required=False, error_messages={
                                     'invalid': 'Solo archivos para imagenes'}, widget=forms.FileInput)

    class Meta:
        model = Client
        fields = ['profile_image']

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if len(phone) < 9:
            raise ValidationError(
                'El número de teléfono debe tener al menos 9 dígitos.')
        return phone

    def clean_birth_date(self):
        birth_date = self.cleaned_data.get('birth_date')
        today = date.today()
        age = today.year - birth_date.year - \
            ((today.month, today.day) < (birth_date.month, birth_date.day))

        if age < 18:
            raise ValidationError('Debes ser mayor de edad para registrarte.')

        return birth_date


class AgencyForm(forms.ModelForm):
    """
    Author: Santiago Mendivil
    Form for creating or updating an Agency instance.
    Fields:
        profile_image (ImageField): Optional field for uploading an image file.
        agency_name (CharField): Name of the agency.
        agency_description (CharField): Description of the agency.
        state (CharField): State where the agency is located.
        address (CharField): Address of the agency.
        suburb (CharField): Suburb where the agency is located.
        town (CharField): Town where the agency is located.
        phone (CharField): Phone number of the agency.
        zip_code (CharField): ZIP code of the agency.
        certificate (FileField): Certificate file for the agency.
    Methods:
        __init__(*args, **kwargs): Initializes the form and adds 'form-control' class to all fields.
        clean_phone(): Validates that the phone number has at least 9 digits.
    """
    profile_image = forms.ImageField(
        required=False,
        error_messages={'invalid': 'Solo archivos de imagen son permitidos'},
        widget=forms.FileInput
    )

    class Meta:
        model = Agency
        fields = [
            'agency_name', 'agency_description', 'state', 'address',
            'suburb', 'town', 'phone', 'zip_code', 'profile_image', 'cover_photo'
        ]

    def __init__(self, *args, **kwargs):
        super(AgencyForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone and len(phone) < 9:
            raise ValidationError(
                'El número de teléfono debe tener al menos 9 dígitos.')
        return phone


class AgencyProfileForm(forms.ModelForm):
    """
    Author: Santiago Mendivil
    Form for creating and updating an agency profile.
    Fields:
        profile_image (ImageField): Optional image field for the agency's profile picture.
        agency_name (CharField): Name of the agency.
        agency_description (TextField): Description of the agency.
        state (CharField): State where the agency is located.
        address (CharField): Address of the agency.
        suburb (CharField): Suburb where the agency is located.
        town (CharField): Town where the agency is located.
        phone (CharField): Phone number of the agency.
        zip_code (CharField): ZIP code of the agency's location.
    Methods:
        __init__(*args, **kwargs): Initializes the form and sets the CSS class for each field to 'form-control'.
        clean_phone(): Validates that the phone number has at least 9 digits.
    Meta:
        model (Agency): The model that this form is associated with.
        fields (list): List of fields to include in the form.
    """
    profile_image = forms.ImageField(required=False, error_messages={
                                     'invalid': 'Solo archivos para imagenes'}, widget=forms.FileInput)
    cover_photo = forms.ImageField(required=False, error_messages={
                                   'invalid': 'Solo archivos para imagenes'}, widget=forms.FileInput)

    class Meta:
        model = Agency
        fields = ['agency_name', 'agency_description', 'state', 'address',
                  'suburb', 'town', 'phone', 'zip_code', 'profile_image', 'cover_photo']

    def __init__(self, *args, **kwargs):
        super(AgencyProfileForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if len(phone) < 9:
            raise ValidationError(
                'El número de teléfono debe tener al menos 9 dígitos.')
        return phone
