from django.shortcuts import render
from django.http import HttpResponse
from datetime import datetime
from django.shortcuts import render, get_object_or_404, redirect
from apps.appTour.models import Tour
from decimal import Decimal
from .forms import ReservationForm



def payment(request):
    return render(request, 'payment.html')


def detalles_reservacion(request, tour_id):
    tour = get_object_or_404(Tour, id=tour_id)

    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            number_people = form.cleaned_data['number_people']
            total_price = Decimal(number_people) * tour.price_per_person

            # Guarda los valores en la sesión
            request.session['total_price'] = float(total_price)  # Convierte a float para evitar problemas de serialización
            request.session['number_people'] = number_people

            # Redirecciona a la vista de pago
            return redirect('pago_reservacion', tour_id=tour_id)
    else:
        form = ReservationForm()  # Inicializa el formulario con el valor predeterminado

    context = {
        'reservation_date': datetime.now(),
        'tour': tour,
        'form': form
    }
    return render(request, 'detalles_reservacion.html', context)


def pago_reservacion(request, tour_id):
    tour = get_object_or_404(Tour, id=tour_id)

    if request.method == 'POST':
        total_price = request.POST.get('total_price')
        number_people = request.POST.get('number_people')
    else:
        total_price = request.session.get('total_price', float(tour.price_per_person))
        number_people = request.session.get('number_people', 1)

    context = {
        'tour': tour,
        'total_price': total_price,
        'number_people': number_people
    }
    return render(request, 'pago_reservacion.html', context)

def final_reservacion(request):
    return render(request, 'final_reservacion.html')
