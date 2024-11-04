from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
import json
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

# Importación de modelos
from .models import Payments, PaymentMethod
from apps.appTour.models import Reservation
from apps.appUser.models import Agency, Client
from apps.appTour.models import Tour

# Para la implementación de Stripe
import stripe
from django.conf import settings
stripe.api_key = settings.STRIPE_SECRET_KEY

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

def realizar_pago_stripe(request):
    if request.method == 'POST':
        tour_id = request.POST.get('tour_id')
        number_people = int(request.POST.get('number_people', 1))

        # Verificar que tour_id no sea None
        if not tour_id:
            return redirect('index')  # O muestra un mensaje de error adecuado

        tour = get_object_or_404(Tour, id=tour_id)
        total_price = float(tour.price_per_person) * number_people

        context = {
            'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
            'tour': tour,
            'number_people': number_people,
            'total_price': total_price,
        }
        return render(request, 'realizar_pago_stripe.html', context)
    else:
        return redirect('detalles_reservacion', id=request.GET.get('tour_id', ''))




def create_payment(request, reservation_id):
    reservation = Reservation.objects.get(id=reservation_id)
    client = reservation.client
    agency = reservation.tour.agency

    # Suponiendo que ya tienes el PaymentMethod del cliente
    payment_method = PaymentMethod.objects.get(client=client)

    # Crear un PaymentIntent
    try:
        payment_intent = stripe.PaymentIntent.create(
            amount=int(reservation.total_price * 100),  # Monto en centavos
            currency='mxn',
            customer=client.stripe_customer_id,
            payment_method=payment_method.stripe_payment_method_id,
            off_session=True,
            confirm=True,
            application_fee_amount=int(reservation.total_price * 0.1 * 100),  # Comisión del 10%
            transfer_data={
                'destination': agency.stripe_agency_id,
            },
            automatic_payment_methods={
                'enabled': True  # Configuración de métodos automáticos
            },
            # return_url solo si es necesario
            return_url='http://127.0.0.1:8000/payment/pago_completado',
        )

        # Crear un registro de pago
        Payments.objects.create(
            client=client,
            agency=agency,
            reservation=reservation,
            payment_method=payment_method,
            amount=reservation.total_price,
            status='completado' if payment_intent.status == 'succeeded' else 'fallado',
        )

        # Redirigir o renderizar una plantilla
        return redirect('index')

    except stripe.error.InvalidRequestError as e:
        # Manejar errores de solicitud
        return JsonResponse({'error': f'Error en la solicitud: {e.user_message}'}, status=400)



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

@csrf_exempt
def process_payment(request):
    data = json.loads(request.body)
    payment_method_id = data['payment_method_id']
    tour_id = data['tour_id']
    number_people = data['number_people']
    total_price = data['total_price']

    # Obtener el cliente
    user = request.user
    if not user.is_authenticated:
        return JsonResponse({'error': 'Usuario no autenticado'}, status=401)

    try:
        client = Client.objects.get(user=user)
    except Client.DoesNotExist:
        return JsonResponse({'error': 'Cliente no encontrado'}, status=400)

    # Asociar el PaymentMethod al cliente en Stripe
    stripe.PaymentMethod.attach(
        payment_method_id,
        customer=client.stripe_customer_id,
    )

    # Actualizar el método de pago predeterminado del cliente
    stripe.Customer.modify(
        client.stripe_customer_id,
        invoice_settings={
            'default_payment_method': payment_method_id,
        },
    )

    # Obtener el tour y la agencia
    tour = get_object_or_404(Tour, id=tour_id)
    agency = tour.agency

    # Obtener o crear el método de pago del cliente en tu base de datos
    try:
        payment_method = PaymentMethod.objects.get(stripe_payment_method_id=payment_method_id)
    except PaymentMethod.DoesNotExist:
        payment_method = PaymentMethod.objects.create(
            client=client,
            stripe_payment_method_id=payment_method_id
        )

    # Crear el PaymentIntent con `automatic_payment_methods` configurado
    try:
        payment_intent = stripe.PaymentIntent.create(
            amount=int(float(total_price) * 100),  # Convertir a centavos
            currency='mxn',
            customer=client.stripe_customer_id,
            payment_method=payment_method_id,
            confirm=True,
            application_fee_amount=int(float(total_price) * 0.1 * 100),  # Comisión del 10%
            transfer_data={
                'destination': agency.stripe_agency_id,
            },
            automatic_payment_methods={
                'enabled': True  # Habilitar métodos de pago automáticos
            },
            # Agrega el return_url solo si es realmente necesario
            return_url='http://127.0.0.1:8000/payment/pago_completado',  # URL accesible para redireccionar al usuario
        )

        # Crea la reservación
        reservation = Reservation.objects.create(
            tour=tour,
            client=client,
            number_people=number_people,
            total_price=total_price,
        )

        # Crea el pago
        Payments.objects.create(
            client=client,
            agency=agency,
            reservation=reservation,
            payment_method=payment_method,  # Asegúrate de asignar el payment_method aquí
            amount=total_price,
            status='pendiente',
            payment_intent_id=payment_intent.id,
        )

        return JsonResponse({'status': 'success'})
    except stripe.error.CardError as e:
        return JsonResponse({'error': str(e)}, status=400)
    except stripe.error.InvalidRequestError as e:
        # Manejo detallado de errores de `InvalidRequestError`
        return JsonResponse({'error': f'Invalid request: {e.user_message}'}, status=400)


def pago_completado(request):
    return render(request, 'pago_completado.html')
