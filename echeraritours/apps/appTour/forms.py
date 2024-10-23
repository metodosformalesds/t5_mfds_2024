from django import forms
from .models import Tour

class TourFilterForm(forms.Form):
    place_of_origin = forms.CharField(
        max_length=100, 
        required=False, 
        label='Punto de partida',
        widget=forms.TextInput(attrs={
            'placeholder': 'Elige tu punto de partida'
        })
    )
    destination_place = forms.CharField(
        max_length=100, 
        required=False, 
        label='Destino',
        widget=forms.TextInput(attrs={
            'placeholder': 'Elige tu destino'
        })
    )
    start_date = forms.DateField(
        required=False, 
        label='Fecha (YYYY-MM-DD)',
        widget=forms.DateInput(attrs={
            'type': 'date', 
            'placeholder': 'YYYY-MM-DD'
        }),
        input_formats=['%Y-%m-%d']
    )