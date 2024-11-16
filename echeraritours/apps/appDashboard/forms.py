from django import forms
from django.core.exceptions import ValidationError
from apps.appUser.models import Client, Agency
from apps.appTour.models import Reviews


class UserForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['first_name', 'maternal_surname', 'paternal_surname', 'city',
                  'phone', 'birth_date', 'zip_code', 'identification', 'profile_image']

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if len(phone) < 9:
            raise ValidationError(
                'El número de teléfono debe tener al menos 9 dígitos.')
        return phone


class UserProfileForm(forms.ModelForm):
    profile_image = forms.ImageField(required=False, error_messages={
                                     'invalid': 'Solo archivos para imagenes'}, widget=forms.FileInput)

    class Meta:
        model = Client
        fields = ['first_name', 'maternal_surname', 'paternal_surname', 'city',
                  'phone', 'birth_date', 'zip_code', 'identification', 'profile_image']

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


class AgencyForm(forms.ModelForm):
    profile_image = forms.ImageField(
        required=False,
        error_messages={'invalid': 'Solo archivos de imagen son permitidos'},
        widget=forms.FileInput
    )

    class Meta:
        model = Agency
        fields = [
            'agency_name', 'agency_description', 'state', 'address',
            'suburb', 'town', 'phone', 'zip_code', 'certificate', 'profile_image'
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
    profile_image = forms.ImageField(required=False, error_messages={
                                     'invalid': 'Solo archivos para imagenes'}, widget=forms.FileInput)

    class Meta:
        model = Agency
        fields = ['agency_name', 'agency_description', 'state', 'address',
                  'suburb', 'town', 'phone', 'zip_code', 'profile_image']

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
