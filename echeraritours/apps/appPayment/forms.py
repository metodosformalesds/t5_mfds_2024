from django import forms

class ReservationForm(forms.Form):
    number_people = forms.IntegerField(
        min_value=1,
        label="Número de personas",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'value': 1})
    )
