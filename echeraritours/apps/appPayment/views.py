from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from decimal import Decimal
from django.conf import settings
from django.urls import reverse
from django.contrib import messages
import paypalrestsdk
from paypalrestsdk import Payment
from .models import Payments, PaymentMethod
from apps.appTour.models import Reservation, Tour
from apps.appUser.models import Agency, Client
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
import stripe
import json

# Configurar Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


def detalles_reservacion(request, id):
    tour = get_object_or_404(Tour, id=id)
    current_date = timezone.now()
    reservations = Reservation.objects.filter(tour=tour).count()
    available_bookings = tour.capacity - reservations
    context = {
        'tour': tour,
        'current_date': current_date,
        'reservations': reservations,
        'available_bookings': available_bookings,
    }
    return render(request, 'detalles_reservacion.html', context)


def seleccion_pago(request, id):
    """
    Función intermedia para seleccionar el método de pago.
    """
    tour = get_object_or_404(Tour, id=id)
    current_date = timezone.now()
    number_people = int(request.POST.get('number_people', 1))
    total_price = float(request.POST.get(
        'total_price', tour.price_per_person * number_people))

    context = {
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
        'paypal_client_id': settings.PAYPAL_CLIENT_ID,
        'tour': tour,
        'current_date': current_date,
        'total_price': total_price,
        'number_people': number_people
    }
    return render(request, 'seleccion_pago.html', context)


def realizar_pago_paypal(request, id):
    tour = get_object_or_404(Tour, id=id)
    number_people = int(request.POST.get('number_people', 1))
    total_price = Decimal(tour.price_per_person) * Decimal(number_people)

    # Crear un objeto de pago con PayPal
    payment = Payment({
        "intent": "sale",
        "payer": {
            "payment_method": "paypal"
        },
        "redirect_urls": {
            "return_url": request.build_absolute_uri(reverse('pago_completado')),
            "cancel_url": request.build_absolute_uri(reverse('pago_cancelado'))
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

    if payment.create():
        # Guardar el ID de la reservación en la sesión si es necesario
        request.session['tour_id'] = tour.id
        request.session['number_people'] = number_people
        request.session['total_price'] = str(total_price)

        for link in payment.links:
            if link.rel == "approval_url":
                return redirect(link.href)
    else:
        messages.error(request, "Error al crear el pago con PayPal")
        return redirect('seleccion_pago', id=id)


def realizar_pago_stripe(request, id):
    if request.method == 'GET':
        tour = get_object_or_404(Tour, id=id)
        number_people = int(request.GET.get('number_people', 1))
        total_price = float(tour.price_per_person) * number_people
        
        # Obtener métodos de pago guardados
        client = Client.objects.get(user=request.user)
        saved_payment_methods = PaymentMethod.objects.filter(client=client)

        context = {
            'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
            'tour': tour,
            'number_people': number_people,
            'total_price': total_price,
            'saved_payment_methods': saved_payment_methods,
        }
        return render(request, 'realizar_pago_stripe.html', context)
    else:
        return redirect('seleccion_pago', id=id)


@csrf_exempt
def process_payment(request):
    data = json.loads(request.body)
    tour_id = data['tour_id']
    number_people = int(data['number_people'])
    total_price = float(data['total_price'])

    user = request.user
    if not user.is_authenticated:
        return JsonResponse({'error': 'Usuario no autenticado'}, status=401)

    try:
        client = Client.objects.get(user=user)
    except Client.DoesNotExist:
        return JsonResponse({'error': 'Cliente no encontrado'}, status=400)

    # Obtener o crear cliente de Stripe
    if not client.stripe_customer_id:
        stripe_customer = stripe.Customer.create(
            email=user.email,
            name=f"{user.first_name} {user.last_name}",
        )
        client.stripe_customer_id = stripe_customer.id
        client.save()

    payment_method_id = data.get('selected_payment_method_id') or data.get('payment_method_id')

    if not payment_method_id:
        return JsonResponse({'error': 'Método de pago no proporcionado'}, status=400)

    # Crear la reserva y realizar el pago con el método seleccionado
    tour = get_object_or_404(Tour, id=tour_id)
    reservation = Reservation.objects.create(
        tour=tour,
        client=client,
        number_people=number_people,
        total_price=total_price,
    )

    try:
        payment_intent = stripe.PaymentIntent.create(
            amount=int(total_price * 100),
            currency='mxn',
            customer=client.stripe_customer_id,
            payment_method=payment_method_id,
            confirm=True,
            application_fee_amount=int(total_price * 0.1 * 100),
            transfer_data={'destination': tour.agency.stripe_agency_id},
            payment_method_types=['card'],
        )

        Payments.objects.create(
            client=client,
            agency=tour.agency,
            reservation=reservation,
            payment_method=PaymentMethod.objects.get(stripe_payment_method_id=payment_method_id),
            amount=total_price,
            status='completado' if payment_intent.status == 'succeeded' else 'pendiente',
            payment_intent_id=payment_intent.id,
        )

        return JsonResponse({'status': 'success'})

    except stripe.error.CardError as e:
        return JsonResponse({'error': 'Error en el pago: ' + str(e)}, status=400)
    except stripe.error.StripeError as e:
        return JsonResponse({'error': 'Error en Stripe: ' + str(e)}, status=400)
    except Exception as e:
        return JsonResponse({'error': 'Ocurrió un error inesperado: ' + str(e)}, status=500)



def pago_cancelado(request):
    # Limpiar la información de la sesión si es necesario
    if 'tour_id' in request.session:
        del request.session['tour_id']
    if 'number_people' in request.session:
        del request.session['number_people']
    if 'total_price' in request.session:
        del request.session['total_price']

    messages.warning(request, "Has cancelado el pago. Tu reservación no ha sido confirmada.")
    return redirect('index.html')


def pago_completado(request):
    return render(request, 'pago_completado.html')


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Payload inválido
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Firma inválida
        return HttpResponse(status=400)

    # Manejar el evento
    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']

        # Actualiza el estado del pago en tu base de datos
        payment_intent_id = payment_intent['id']
        try:
            payment = Payments.objects.get(payment_intent_id=payment_intent_id)
            payment.status = 'completado'
            payment.save()
        except Payments.DoesNotExist:
            pass

    return HttpResponse(status=200)
