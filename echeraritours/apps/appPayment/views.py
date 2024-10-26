from django.shortcuts import render
from django.http import HttpResponse
from datetime import datetime 

def payment(request):
    return render(request, 'payment.html')

def detalles_reservacion(request):
    context = {
        'reservation_date': datetime.now(),  # or actual reservation data
        'tour': {
            'start_date': '2024-12-01',  # Replace with actual data
            'end_date': '2024-12-07',  # Replace with actual data
            'available_capacity': 10,  # Replace with dynamic data
            'price_per_person': 200,  # Replace with actual price
            'image_url': '/path/to/image',  # Replace with dynamic image URL
            'title': 'Amazing Tour'  # Replace with actual title
        },
        'reservation': {
            'number_people': 2  # Replace with actual reservation details
        },
        'total_price': 400  # Replace with calculated total price
    }
    return render(request, 'detalles_reservacion.html')


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
