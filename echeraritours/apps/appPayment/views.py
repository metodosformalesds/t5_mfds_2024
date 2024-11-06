from django.http import HttpResponse
from datetime import datetime
from django.shortcuts import render, get_object_or_404, redirect
from decimal import Decimal
from .forms import ReservationForm
from django.conf import settings
from django.urls import reverse
from django.contrib import messages
from paypalrestsdk import Payment
from .paypal import paypalrestsdk
from apps.appTour.models import Reservation, Tour

def pago_exitoso_view(request):
    payment_id = request.GET.get("paymentId")
    payer_id = request.GET.get("PayerID")
    
    # Recupera el reservation_id de la sesión
    reservation_id = request.session.get('reservation_id')
    
    # Ejecutar el pago en PayPal
    pago = Payment.find(payment_id)
    if pago.execute({"payer_id": payer_id}):
        messages.success(request, "Pago completado con éxito")
        # Aquí puedes marcar la reservación como pagada y realizar otras acciones necesarias
        return redirect("tour_home")  # Redirige a la página principal o la deseada
    else:
        messages.error(request, "Error al confirmar el pago")
        return redirect("detalle_reservacion", reservation_id=reservation_id)

def pago_cancelado_view(request):
    # Recupera el reservation_id de la sesión
    reservation_id = request.session.get('reservation_id')
    
    messages.info(request, "El pago fue cancelado.")
    return redirect("detalle_reservacion", reservation_id=reservation_id)


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
        metodo_pago = request.POST.get('payment_method')
        number_people = int(request.POST.get('number_people', 1))
        total_price = Decimal(number_people) * tour.price_per_person

        client = request.user.client if hasattr(request.user, 'client') else None

        if client:
            reservation = Reservation(
                tour=tour,
                client=client,
                number_people=number_people,
                total_price=total_price
            )

            try:
                reservation.save()
                messages.success(request, "Reservación realizada exitosamente.")
                request.session['reservation_id'] = reservation.id

                if metodo_pago == 'paypal':
                    pago = Payment({
                        "intent": "sale",
                        "payer": {
                            "payment_method": "paypal"
                        },
                        "redirect_urls": {
                            "return_url": request.build_absolute_uri(reverse("pago_exitoso")),
                            "cancel_url": request.build_absolute_uri(reverse("pago_cancelado")),
                        },
                        "transactions": [{
                            "item_list": {
                                "items": [{
                                    "name": reservation.tour.title,
                                    "sku": str(reservation.tour.id),
                                    "price": f"{total_price:.2f}",
                                    "currency": "MXN",
                                    "quantity": number_people,
                                }]
                            },
                            "amount": {
                                "total": f"{total_price:.2f}",
                                "currency": "MXN"
                            },
                            "description": f"Reservación para el tour: {reservation.tour.title}"
                        }]
                    })

                    if pago.create():
                        print("Pago creado exitosamente en PayPal.")
                        for link in pago.links:
                            if link.method == "REDIRECT":  # Corregido el error tipográfico
                                print("Redirigiendo a PayPal URL:", link.href)
                                return redirect(link.href)
                    else:
                        print("Error al crear el pago en PayPal:", pago.error)
                        messages.error(request, "Error al crear el pago con PayPal.")
                        return redirect("detalles_reservacion", tour_id=tour.id)
                else:
                    messages.info(request, "Procesando pago con tarjeta.")
                    return redirect('final_reservacion')

            except ValueError as e:
                messages.error(request, str(e))
        else:
            messages.error(request, "No se encontró un cliente asociado a esta cuenta.")

    else:
        total_price = Decimal(request.session.get('total_price', float(tour.price_per_person)))
        number_people = int(request.session.get('number_people', 1))

    context = {
        'tour': tour,
        'total_price': total_price,
        'number_people': number_people
    }
    return render(request, 'pago_reservacion.html', context)

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
