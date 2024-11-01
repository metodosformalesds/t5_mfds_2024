from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.utils import timezone
from apps.appTour.models import Tour


def payment(request):
    return render(request, 'payment.html')


def detalles_reservacion(request, id):
    tour = get_object_or_404(Tour, id=id)
    current_date = timezone.now()
    return render(request, 'detalles_reservacion.html', {'tour': tour, 'current_date': current_date})


def pago_reservacion(request):
    tour = {
        'title': 'Cancún: El Paraíso del Caribe Mexicano',
        'start_date': '23 de Agosto del 2024',
        'price_per_person': 4800,
        'image_url': 'path_to_image.jpg'
    }

    total_price = 4800

    context = {
        'tour': tour,
        'total_price': total_price
    }

    return render(request, 'pago_reservacion.html', context)


def final_reservacion(request):
    return render(request, 'final_reservacion.html')
