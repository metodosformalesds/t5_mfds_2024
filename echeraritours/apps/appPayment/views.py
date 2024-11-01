from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.utils import timezone
from apps.appTour.models import Tour


def payment(request):
    """
    Handles the payment view.

    This view renders the payment page when a request is made.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The rendered payment page.
    """
    return render(request, 'payment.html')


def detalles_reservacion(request, id):
    """
    Handles the request to display the details of a specific tour reservation.

    Args:
        request (HttpRequest): The HTTP request object.
        id (int): The ID of the tour reservation to retrieve.

    Returns:
        HttpResponse: The rendered HTML page displaying the tour reservation details.
    """
    tour = get_object_or_404(Tour, id=id)
    current_date = timezone.now()
    return render(request, 'detalles_reservacion.html', {'tour': tour, 'current_date': current_date})


def pago_reservacion(request):
    """
    Handles the payment reservation view.

    This view renders the 'pago_reservacion.html' template when a request is made.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The rendered 'pago_reservacion.html' template.
    """
    return render(request, 'pago_reservacion.html')


def final_reservacion(request):
    """
    Handles the final reservation view.

    This view renders the 'final_reservacion.html' template when a request is made.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The rendered 'final_reservacion.html' template.
    """
    return render(request, 'final_reservacion.html')
