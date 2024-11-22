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
    """
    Author: Neida Franco 
    View function to display the details of a specific tour reservation.
    Args:
        request (HttpRequest): The HTTP request object.
        id (int): The ID of the tour.
    Returns:
        HttpResponse: The rendered HTML page with the tour details, current date, 
                      number of reservations, and available bookings.
    Raises:
        Http404: If the tour with the given ID does not exist.
    """

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
    Author: Leonardo Ortega, Hector Ramos
    Handles the selection of a payment method for a tour.
        This view function retrieves the tour details, calculates the total price based on the number of people,
        and fetches any saved payment methods for the authenticated user. It then renders the payment selection page
        with the relevant context.
        Args:
            request (HttpRequest): The HTTP request object containing POST data.
            id (int): The ID of the tour to be booked.
        Returns:
            HttpResponse: The rendered payment selection page with the context data.
        Context:
            stripe_public_key (str): The public key for Stripe payments.
            paypal_client_id (str): The client ID for PayPal payments.
            tour (Tour): The tour object being booked.
            current_date (datetime): The current date and time.
            total_price (float): The total price for the tour based on the number of people.
            number_people (int): The number of people for the tour.
            saved_payment_methods (QuerySet or None): The saved payment methods for the authenticated user, if any.    
    """
    tour = get_object_or_404(Tour, id=id)
    current_date = timezone.now()
    number_people = int(request.POST.get('number_people', 1))
    total_price = float(request.POST.get(
        'total_price', tour.price_per_person * number_people))

    user = request.user
    if user.is_authenticated:
        try:
            client = Client.objects.get(user=user)
            saved_payment_methods = PaymentMethod.objects.filter(client=client)
        except Client.DoesNotExist:
            saved_payment_methods = None
    else:
        saved_payment_methods = None

    context = {
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
        'paypal_client_id': settings.PAYPAL_CLIENT_ID,
        'tour': tour,
        'current_date': current_date,
        'total_price': total_price,
        'number_people': number_people,
        'saved_payment_methods': saved_payment_methods,
    }
    return render(request, 'seleccion_pago.html', context)


def realizar_pago_paypal(request, id):
    """
    Authors: Neida Franco, Leonardo Ortega
    Handle the PayPal payment process for a tour reservation.
    This view function processes a POST request to create a PayPal payment for a tour.
    It retrieves the tour details, calculates the total price based on the number of people,
    and creates a PayPal payment object. If the payment is successfully created, it redirects
    the user to the PayPal approval URL. If the payment creation fails, it redirects the user
    back to the payment selection page with an error message.
    Args:
        request (HttpRequest): The HTTP request object.
        id (int): The ID of the tour to be reserved.
    Returns:
        HttpResponse: A redirect to the PayPal approval URL if the payment is created successfully,
                      or a redirect to the payment selection page if the request method is not POST
                      or if there is an error in creating the payment.
    """
    if request.method == 'POST':
        # Obtener el tour y los valores enviados por el formulario
        tour = get_object_or_404(Tour, id=id)
        number_people = int(request.POST.get('number_people', 1))
        price_per_person = Decimal(tour.price_per_person).quantize(Decimal('0.01'))
        total_price = (price_per_person * Decimal(number_people)).quantize(Decimal('0.01'))

        # Crear un objeto de pago con PayPal usando los datos del contexto
        payment = Payment({
            "intent": "sale",
            "payer": {
                "payment_method": "paypal"
            },
            "redirect_urls": {
                "return_url": request.build_absolute_uri(reverse('completar_pago_paypal')),
                "cancel_url": request.build_absolute_uri(reverse('pago_cancelado'))
            },
            "transactions": [{
                "item_list": {
                    "items": [{
                        "name": tour.title,
                        "sku": "001",
                        # Debe ser string con dos decimales
                        "price": f"{price_per_person:.2f}",
                        "currency": "MXN",
                        "quantity": number_people
                    }]
                },
                "amount": {
                    # Debe ser string con dos decimales
                    "total": f"{total_price:.2f}",
                    "currency": "MXN"
                },
                "description": f"Reserva para el tour: {tour.title}"
            }]
        })

        if payment.create():
            print("Pago creado con éxito:", payment.id)
            request.session['tour_id'] = tour.id
            request.session['number_people'] = number_people
            request.session['total_price'] = str(total_price)

            for link in payment.links:
                if link.rel == "approval_url":
                    return redirect(link.href)
        else:
            messages.error(request, "Error al crear el pago con PayPal")
            return redirect('seleccion_pago', id=id)

    # Si la solicitud no es POST, redirige a la página de selección de pago
    return redirect('seleccion_pago', id=id)


def realizar_pago_stripe(request, id):
    """
    Author: Hector Ramos
    Handle the payment process using Stripe.
    This view function handles both displaying the payment page and processing the payment.
    If the request method is GET, it retrieves the tour information and calculates the total price
    based on the number of people. It then renders the payment page with the necessary context.
    If the request method is not GET, it redirects to the payment selection page.
    Args:
        request (HttpRequest): The HTTP request object.
        id (int): The ID of the tour to be paid for.
    Returns:
        HttpResponse: The rendered payment page if the request method is GET.
        HttpResponseRedirect: A redirect to the payment selection page if the request method is not GET.
    """
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
    """
    Authors: Hector Ramos, Santiago Mendivil
    Processes a payment for a tour reservation.
    This function handles the payment process for a tour reservation using Stripe. It performs the following steps:
    1. Parses the request body to extract payment details.
    2. Authenticates the user and retrieves the associated client.
    3. Creates or retrieves the Stripe customer for the client.
    4. Attaches the provided payment method to the Stripe customer.
    5. Updates the default payment method for the Stripe customer.
    6. Retrieves the tour and associated agency.
    7. Creates or retrieves the payment method in the local database.
    8. Creates a reservation for the tour.
    9. Creates a PaymentIntent with Stripe and handles the payment process.
    10. Creates a payment record in the local database.
    Args:
        request (HttpRequest): The HTTP request containing the payment details.
    Returns:
        JsonResponse: A JSON response indicating the success or failure of the payment process.
    """
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


def pago_cancelado(request):
    """
    Author: Hector Ramos
    Handles the cancellation of a payment.
    This view function performs the following actions:
    1. Clears specific session information related to the tour reservation.
    2. Displays a warning message to the user indicating that the payment has been canceled.
    3. Redirects the user to the index page.
    Args:
        request (HttpRequest): The HTTP request object containing session data.
    Returns:
        HttpResponseRedirect: A redirect response to the index page.
    """
    # Limpiar la información de la sesión si es necesario
    if 'tour_id' in request.session:
        del request.session['tour_id']
    if 'number_people' in request.session:
        del request.session['number_people']
    if 'total_price' in request.session:
        del request.session['total_price']

    messages.warning(
        request, "Has cancelado el pago. Tu reservación no ha sido confirmada.")
    return redirect('index.html')


def completar_pago_paypal(request):
    """
    Author: Leonardo Ortega, Neida Franco
    Completa el proceso de pago utilizando PayPal.
    Args:
        request (HttpRequest): La solicitud HTTP que contiene los datos necesarios para completar el pago.
    Returns:
        HttpResponse: Redirige a la página de confirmación de pago si el pago es exitoso,
                      de lo contrario redirige a la página de selección de pago o de pago cancelado.
    Maneja los siguientes pasos:
        1. Recupera los datos de la sesión necesarios para completar el pago.
        2. Verifica que los datos de la sesión sean válidos y completos.
        3. Convierte los valores de la sesión al tipo adecuado.
        4. Obtiene el tour y el cliente asociados con la solicitud.
        5. Recupera el pago de PayPal utilizando el ID de pago.
        6. Ejecuta el pago de PayPal.
        7. Crea una reservación si el pago es exitoso.
        8. Redirige a la página de confirmación de pago o maneja errores en caso de fallos.
    Excepciones:
        ValueError, TypeError: Si hay un error en la conversión de los datos de la sesión.
        Exception: Si ocurre cualquier otro error durante la ejecución del pago.
    """
    # Recuperar los datos de la sesión
    payment_id = request.GET.get('paymentId')
    payer_id = request.GET.get('PayerID')
    tour_id = request.session.get('tour_id')
    number_people = request.session.get('number_people')
    total_price = request.session.get('total_price')

    # Verificar que los datos de la sesión existan
    if not (payment_id and payer_id and tour_id and number_people and total_price):
        messages.error(request, "Datos de la sesión no válidos o incompletos.")
        return redirect('seleccion_pago')

    try:
        # Convertir los valores al tipo adecuado
        number_people = int(number_people)
        total_price = Decimal(total_price).quantize(Decimal('0.01'))
    except (ValueError, TypeError):
        messages.error(request, "Error en la conversión de los datos.")
        return redirect('seleccion_pago')

    # Obtener el tour y el cliente
    tour = get_object_or_404(Tour, id=tour_id)
    client = get_object_or_404(Client, user=request.user)

    # Recuperar el pago de PayPal
    payment = paypalrestsdk.Payment.find(payment_id)

    try:
        if payment.execute({"payer_id": payer_id}):  # Ejecuta el pago
            # Crear la reservación
            reservation = Reservation.objects.create(
                tour=tour,
                client=client,
                number_people=number_people,
                total_price=total_price,
            )

            # Redirige a la página de confirmación con la reservación
            messages.success(request, "El pago se hizo correctamente")
            return render(request, 'pago_completado.html', {'reservation': reservation})
        else:
            messages.error(request, "El pago no pudo completarse con PayPal.")
            return redirect('pago_cancelado')
    except Exception as e:
        # Maneja cualquier excepción durante la ejecución del pago
        messages.error(request, f"Error al ejecutar el pago: {str(e)}")
        return redirect('pago_cancelado')


def pago_completado(request):
    """
    Author: Leonardo Ortega
    Handles the completion of a payment process.

    This view function renders the 'pago_completado.html' template when a payment
    process is completed successfully.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The rendered 'pago_completado.html' template.
    """
    return render(request, 'pago_completado.html')


@csrf_exempt
def stripe_webhook(request):
    """
    Authors: Hector Ramos, Santiago Mendivil
    Handle Stripe webhook events.
    This view processes incoming webhook events from Stripe. It verifies the
    event's signature to ensure its authenticity and then handles specific
    event types, such as 'payment_intent.succeeded'.
    Args:
        request (HttpRequest): The HTTP request object containing the webhook payload.
    Returns:
        HttpResponse: A response with status 200 if the event is successfully processed,
                      or status 400 if there is an error with the payload or signature.
    Raises:
        ValueError: If the payload is invalid.
        stripe.error.SignatureVerificationError: If the signature verification fails.
    """
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
