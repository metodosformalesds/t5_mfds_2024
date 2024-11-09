from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from decimal import Decimal
from django.conf import settings
from django.urls import reverse
from django.contrib import messages
from paypalrestsdk import Payment
from .models import Payments
from apps.appTour.models import Reservation, Tour
from django.utils import timezone


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



def detalles_reservacion(request, id):
    tour = get_object_or_404(Tour, id=id)
    current_date = timezone.now()
    return render(request, 'detalles_reservacion.html', {'tour': tour, 'current_date': current_date})

def seleccion_pago(request, id):
    """
    Función intermedia para seleccionar el método de pago.
    """
    tour = get_object_or_404(Tour, id=id)
    current_date = timezone.now()
    total_price = float(tour.price_per_person) * int(request.GET.get('number_people', 1))

    context = {
        'tour': tour,
        'total_price': total_price,
        'number_people': request.GET.get('number_people', 1)
    }
    return render(request, 'seleccion_pago.html', {'tour': tour, 'current_date': current_date, 'context': context})

def realizar_pago_paypal(request, id):
    if request.method == 'POST':
        number_people = int(request.POST.get('number_people', 1))
        tour = get_object_or_404(Tour, id=id)
        total_price = Decimal(tour.price_per_person) * Decimal(number_people)

        # Crear un objeto de pago con PayPal
        payment = Payment({
            "intent": "sale",
            "payer": {
                "payment_method": "paypal"
            },
            "redirect_urls": {
                "return_url": "http://127.0.0.1:8000/payment/pago_completado",
                "cancel_url": "http://127.0.0.1:8000/payment/cancelado"
            },
            "transactions": [{
                "item_list": {
                    "items": [{
                        "name": tour.title,
                        "sku": "001",
                        "price": f"{tour.price_per_person:.2f}",
                        "currency": "MXN",
                        "quantity": number_people
                    }]
                },
                "amount": {
                    "total": f"{total_price:.2f}",
                    "currency": "MXN"
                },
                "description": f"Reserva para el tour: {tour.title}"
            }]
        })
        
        
    context = {
        'tour': tour,
        'total_price': total_price,
        'number_people': request.GET.get('number_people', 1)
    }
    if payment.create():
            for link in payment.links:
                if link.rel == "approval_url":
                    return redirect(link.href)
    else:
        return JsonResponse({'error': 'Error al crear el pago con PayPal'}, status=400)

    return redirect('detalles_reservacion', id=id)

def realizar_pago_stripe(request, id):
    """
    Lógica para manejar el pago con Stripe.
    Esta función manejará el flujo de pago seguro con Stripe,
    incluyendo la creación de un PaymentIntent y el procesamiento del pago.
    """
    # TODO: Implementar la lógica de Stripe aquí
    # Puedes usar el SDK de Stripe para crear un PaymentIntent
    # y redirigir o procesar el pago como sea necesario
    return HttpResponse("Página de pago con Stripe (en desarrollo)")

def pago_completado(request):
    payment_id = request.GET.get('paymentId')
    payer_id = request.GET.get('PayerID')

    if not payment_id or not payer_id:
        return JsonResponse({'error': 'Datos incompletos de PayPal'}, status=400)

    payment = Payment.find(payment_id)

    if payment.execute({"payer_id": payer_id}):
        # Crear un registro de pago en la base de datos
        Payments.objects.create(
            client=request.user.client,
            amount=payment.transactions[0].amount.total,
            status='completado',
            payment_intent_id=payment.id
        )
        return render(request, 'pago_completado.html')
    else:
        return JsonResponse({'error': 'Error al procesar el pago'}, status=400)
