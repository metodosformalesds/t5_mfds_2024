from django import forms
from .models import Tour


class TourFilterForm(forms.Form):
    """
    TourFilterForm is a Django form used to filter tours based on the place of origin, 
    destination place, and start date.

    Attributes:
        place_of_origin (forms.CharField): An optional field for the starting point of the tour.
            - max_length: 100
            - required: False
            - label: 'Punto de partida'
            - widget: TextInput with a placeholder 'Elige tu punto de partida'

        destination_place (forms.CharField): An optional field for the destination of the tour.
            - max_length: 100
            - required: False
            - label: 'Destino'
            - widget: TextInput with a placeholder 'Elige tu destino'

        start_date (forms.DateField): An optional field for the start date of the tour.
            - required: False
            - label: 'Fecha (YYYY-MM-DD)'
            - widget: DateInput with type 'date' and placeholder 'YYYY-MM-DD'
            - input_formats: ['%Y-%m-%d']
    """
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
