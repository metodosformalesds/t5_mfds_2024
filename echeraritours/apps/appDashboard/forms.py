from django import forms
from apps.appUser.models import Client


class UserForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['first_name', 'maternal_surname', 'paternal_surname', 'city',
                  'phone', 'birth_date', 'zip_code', 'identification', 'profile_image']

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'


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
