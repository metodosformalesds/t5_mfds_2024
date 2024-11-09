from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from decimal import Decimal
from django.conf import settings
from django.urls import reverse
from django.contrib import messages
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
            "return_url": request.build_absolute_uri(reverse('pago_exitoso')),
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
        return redirect('detalles_reservacion', id=id)


def realizar_pago_stripe(request, id):
    if request.method == 'GET':
        # Mostrar la página de pago con Stripe
        tour = get_object_or_404(Tour, id=id)
        number_people = int(request.GET.get('number_people', 1))
        total_price = float(tour.price_per_person) * number_people

        context = {
            'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
            'tour': tour,
            'number_people': number_people,
            'total_price': total_price,
        }
        return render(request, 'realizar_pago_stripe.html', context)
    else:
        # Procesar el pago con Stripe (manejado por la función process_payment)
        return redirect('seleccion_pago', id=id)


@csrf_exempt
def process_payment(request):
    data = json.loads(request.body)
    payment_method_id = data['payment_method_id']
    tour_id = data['tour_id']
    number_people = int(data['number_people'])
    total_price = float(data['total_price'])

    # Obtener el cliente
    user = request.user
    if not user.is_authenticated:
        return JsonResponse({'error': 'Usuario no autenticado'}, status=401)

    try:
        client = Client.objects.get(user=user)
    except Client.DoesNotExist:
        return JsonResponse({'error': 'Cliente no encontrado'}, status=400)

    # Crear o recuperar el cliente de Stripe
    if not client.stripe_customer_id:
        stripe_customer = stripe.Customer.create(
            email=user.email,
            name=f"{user.first_name} {user.last_name}",
        )
        client.stripe_customer_id = stripe_customer.id
        client.save()
    else:
        stripe_customer = stripe.Customer.retrieve(client.stripe_customer_id)

    # Asociar el PaymentMethod al cliente en Stripe
    try:
        stripe.PaymentMethod.attach(
            payment_method_id,
            customer=stripe_customer.id,
        )
    except stripe.error.StripeError as e:
        return JsonResponse({'error': str(e)}, status=400)

    # Actualizar el método de pago predeterminado del cliente
    stripe.Customer.modify(
        stripe_customer.id,
        invoice_settings={
            'default_payment_method': payment_method_id,
        },
    )

    # Obtener el tour y la agencia
    tour = get_object_or_404(Tour, id=tour_id)
    agency = tour.agency

    # Obtener o crear el método de pago del cliente en tu base de datos
    payment_method, created = PaymentMethod.objects.get_or_create(
        client=client,
        stripe_payment_method_id=payment_method_id
    )

    # Crear la reservación
    reservation = Reservation.objects.create(
        tour=tour,
        client=client,
        number_people=number_people,
        total_price=total_price,
    )

    # Crear el PaymentIntent con `automatic_payment_methods` configurado
    try:
        payment_intent = stripe.PaymentIntent.create(
            amount=int(total_price * 100),  # Convertir a centavos
            currency='mxn',
            customer=stripe_customer.id,
            payment_method=payment_method_id,
            confirm=True,
            application_fee_amount=int(
                total_price * 0.1 * 100),  # Comisión del 10%
            transfer_data={
                'destination': agency.stripe_agency_id,
            },
            # Deshabilitar métodos de pago que requieren redirección
            payment_method_types=['card'],  # Solo aceptar pagos con tarjeta
        )

        # Crear un registro de pago
        Payments.objects.create(
            client=client,
            agency=agency,
            reservation=reservation,
            payment_method=payment_method,
            amount=total_price,
            status='completado' if payment_intent.status == 'succeeded' else 'pendiente',
            payment_intent_id=payment_intent.id,
        )

        return JsonResponse({'status': 'success'})
    except stripe.error.CardError as e:
        return JsonResponse({'error': str(e)}, status=400)
    except stripe.error.StripeError as e:
        return JsonResponse({'error': str(e)}, status=400)


def pago_exitoso_view(request):
    payment_id = request.GET.get("paymentId")
    payer_id = request.GET.get("PayerID")

    # Recupera los datos de la sesión
    tour_id = request.session.get('tour_id')
    number_people = request.session.get('number_people')
    total_price = request.session.get('total_price')

    # Ejecutar el pago en PayPal
    pago = Payment.find(payment_id)
    if pago.execute({"payer_id": payer_id}):
        messages.success(request, "Pago completado con éxito")

        # Obtener el usuario y cliente
        user = request.user
        if not user.is_authenticated:
            messages.error(request, "Usuario no autenticado")
            return redirect('detalles_reservacion', id=tour_id)

        try:
            client = Client.objects.get(user=user)
        except Client.DoesNotExist:
            messages.error(request, "Cliente no encontrado")
            return redirect('detalles_reservacion', id=tour_id)

        # Obtener el tour y la agencia
        tour = get_object_or_404(Tour, id=tour_id)
        agency = tour.agency

        # Crear la reservación
        reservation = Reservation.objects.create(
            tour=tour,
            client=client,
            number_people=number_people,
            total_price=total_price,
        )

        # Crear un registro de pago
        Payments.objects.create(
            client=client,
            agency=agency,
            reservation=reservation,
            amount=total_price,
            status='completado',
            payment_intent_id=payment_id,
        )

        # Limpiar la sesión
        del request.session['tour_id']
        del request.session['number_people']
        del request.session['total_price']

        return render(request, 'pago_completado.html')
    else:
        messages.error(request, "Error al confirmar el pago")
        return redirect("detalles_reservacion", id=tour_id)


def pago_cancelado_view(request):
    # Recupera el tour_id de la sesión
    tour_id = request.session.get('tour_id')

    messages.info(request, "El pago fue cancelado.")
    return redirect("detalles_reservacion", id=tour_id)


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
