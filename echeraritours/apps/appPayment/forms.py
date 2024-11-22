from django import forms


class ReservationForm(forms.Form):
    """
    Author: Hector Ramos, Leonardo Ortega
    ReservationForm is a Django form used to handle the reservation details.

    Attributes:
        number_people (forms.IntegerField): An integer field to input the number of people for the reservation.
            - min_value: 1 (minimum number of people allowed)
            - label: "Número de personas" (label for the field)
            - widget: forms.NumberInput with class 'form-control' and default value 1
    """
    number_people = forms.IntegerField(
        min_value=1,
        label="Número de personas",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'value': 1})
    )
