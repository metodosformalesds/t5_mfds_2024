import io
from reportlab.pdfgen import canvas
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from apps.appUser.models import Client, Agency
from apps.appPayment.models import PaymentMethod
from apps.appTour.models import Reservation, Tour, Reviews
from django.views.generic.edit import CreateView, DeleteView
from .forms import UserForm, UserProfileForm, AgencyForm, AgencyProfileForm
from django.contrib import messages
from .models import Reports
from django.urls import reverse_lazy, reverse
from django.db import IntegrityError
import os
from echeraritours import settings
from .models import FavoriteList
from django.utils import timezone
from django import forms
import boto3
from django.views.generic.detail import DetailView
from django.conf import settings
import qrcode
from reportlab.lib.utils import ImageReader
from reportlab.lib.pagesizes import letter
import stripe
from apps.appTour.models import Reservation
from apps.appPayment.models import Payments
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors


stripe.api_key = settings.STRIPE_SECRET_KEY

# Create your views here.

VALID_STATES = [
    'aguascalientes', 'baja california', 'baja california sur', 'campeche', 'chiapas',
    'chihuahua', 'coahuila', 'colima', 'ciudad de méxico', 'durango', 'guanajuato',
    'guerrero', 'hidalgo', 'jalisco', 'méxico', 'michoacán', 'morelos', 'nayarit',
    'nuevo león', 'oaxaca', 'puebla', 'querétaro', 'quintana roo', 'san luis potosí',
    'sinaloa', 'sonora', 'tabasco', 'tamaulipas', 'tlaxcala', 'veracruz', 'yucatán', 'zacatecas'
]


@login_required(login_url='login')
def dashboard(request):
    """
    Author: Santiago Mendivil, Neida Franco
    Redirects the user to the appropriate dashboard based on their role.
    This view checks if the logged-in user is associated with a Client or an Agency.
    If the user is a Client, they are redirected to the client dashboard.
    If the user is an Agency, they are redirected to the agency dashboard.
    If the user is neither, they are redirected to the registration selection page.
    Args:
        request (HttpRequest): The HTTP request object containing user information.
    Returns:
        HttpResponseRedirect: A redirect to the appropriate dashboard or registration selection page.
    """
    user = request.user

    try:
        Client.objects.get(user=user)
        return redirect('client_dashboard')
    except Client.DoesNotExist:
        try:
            Agency.objects.get(user=user)
            return redirect('agency_dashboard')
        except Agency.DoesNotExist:
            return redirect('seleccion_registro')


@login_required(login_url='login')
def client_dashboard(request):
    """
    Author: Leonardo Ortega
    Renders the client dashboard page.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The rendered client dashboard HTML page.
    """
    return render(request, 'client_dashboard.html')


@login_required(login_url='login')
def client_active_plans(request):
    """
    Authors: Neida Franco, Santiago Mendivil
    View function to retrieve and display the active plans of the logged-in client.
    Args:
        request (HttpRequest): The HTTP request object containing metadata about the request.
    Returns:
        HttpResponse: The rendered HTML page displaying the client's active plans.
    The function filters the Reservation objects to get the reservations of the logged-in client
    where the tour's end date is greater than the current time. The filtered reservations are then
    passed to the 'cliente/planes_activos.html' template for rendering.
    """
    current_time = timezone.now()
    reservaciones = Reservation.objects.filter(
        client=request.user.client, tour__end_date__gt=current_time)

    return render(request, 'cliente/planes_activos.html', {'reservaciones': reservaciones})


class PlanDetailView(DetailView):
    """
    Author: Hector Ramos
    A view to display the details of a specific plan.

    Attributes:
        model (Reservation): The model associated with this view.
        template_name (str): The name of the template to be rendered.
        context_object_name (str): The name of the context object to be used in the template.
    """
    model = Reservation
    template_name = 'cliente/detalles_plan.html'
    context_object_name = 'reservacion'
    pk_url_kwarg = 'reservation_pk'


@login_required(login_url='login')
def ticket(request, reservation_pk):
    """
    Author: Santiago Mendivil
    Generates a PDF ticket for a specific reservation.

    Args:
        request (HttpRequest): The HTTP request object.
        reservation_pk (int): The primary key of the reservation for which to generate a ticket.

    Returns:
        HttpResponse: The generated PDF ticket.
    """
    reservation = get_object_or_404(Reservation, pk=reservation_pk)
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Draw border
    p.setLineWidth(2)
    p.rect(50, 50, width - 100, height - 100)

    # Title
    p.setFont("Helvetica-Bold", 20)
    p.drawString(100, height - 100, f"Reservación: {reservation.tour.title}")

    # Subtitle
    p.setFont("Helvetica", 14)
    p.drawString(100, height - 130,
                 f"Folio de reservación: {reservation.folio}")

    # Reservation details
    p.setFont("Helvetica", 12)
    data = [
        ["Cliente", reservation.client.first_name +
            " " + reservation.client.paternal_surname],
        ['Identificador de cliente', reservation.client.identificator],
        ["Tour", reservation.tour.title],
        ["Agencia responsable", reservation.tour.agency.agency_name],
        ["Espacios reservados", reservation.number_people],
        ["Fecha de reservación",
            reservation.reservation_date.strftime('%d/%m/%Y %H:%M')],
        ["Fecha de inicio del tour",
            reservation.tour.start_date.strftime('%d/%m/%Y %H:%M')],
        ["Fecha de fin del tour",
            reservation.tour.end_date.strftime('%d/%m/%Y %H:%M')],
        ["Lugar de origen", reservation.tour.place_of_origin],
        ["Lugar de destino", reservation.tour.destination_place],
        ["Lugar de alojamiento", reservation.tour.lodging_place],
        ["Precio total", f"${reservation.total_price}"],
    ]

    x = 100
    y = height - 160
    for row in data:
        p.drawString(x, y, row[0] + ":")
        p.drawString(x + 200, y, str(row[1]))
        y -= 20

    # Generate QR code
    qr_data = f"Reservación: {reservation.folio}"
    qr = qrcode.make(qr_data)
    qr_buffer = io.BytesIO()
    qr.save(qr_buffer, format='PNG')
    qr_buffer.seek(0)

    # Draw QR code
    qr_image = ImageReader(qr_buffer)
    p.drawImage(qr_image, width - 150, 100, width=100, height=100)

    # Footer
    p.setFont("Helvetica-Oblique", 10)
    p.drawString(100, 70, "Gracias por su preferencia. ¡Disfrute su tour!")

    p.showPage()
    p.save()

    buffer.seek(0)
    return HttpResponse(buffer, content_type='application/pdf')


@ login_required(login_url='login')
def client_profile(request):
    """
    Author: Santiago Mendivil
    Handle the client profile view.
    This view allows a client to view and update their profile information.
    It handles both GET and POST requests. On GET requests, it displays the
    profile forms with the current client information. On POST requests, it
    validates and saves the updated profile information.
    Args:
        request (HttpRequest): The HTTP request object.
    Returns:
        HttpResponse: The rendered client profile page with the profile forms.
    """
    cliente = get_object_or_404(Client, user=request.user)

    if request.method == 'POST':
        user_form = UserForm(request.POST, request.FILES, instance=cliente)
        profile_form = UserProfileForm(
            request.POST, request.FILES, instance=cliente)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()

            messages.success(request, 'Perfil actualizado exitosamente.')
            return redirect('client_profile')
        else:
            messages.error(
                request, f'Por favor corrige los errores a continuación')

    else:
        user_form = UserForm(instance=cliente)
        profile_form = UserProfileForm(instance=cliente)

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'cliente': cliente,
    }
    return render(request, 'cliente/perfil.html', context)


@ login_required(login_url='login')
def favorites(request):
    """
    Author: Santiago Mendivil, Hector Ramos
    View function to display the user's favorite tours.
    If the user is authenticated, retrieves the list of favorite tours for the
    current user and renders the 'cliente/favoritos.html' template with the list
    of tours. If the user is not authenticated, displays an error message and
    redirects to the login page.
    Args:
        request (HttpRequest): The HTTP request object.
    Returns:
        HttpResponse: The rendered 'cliente/favoritos.html' template with the
        list of favorite tours if the user is authenticated, or a redirect to
        the login page if the user is not authenticated.
    """
    if request.user.is_authenticated:
        favorite_list = FavoriteList.objects.filter(
            client=request.user.client).first()
        tours = favorite_list.tours.all() if favorite_list else []

        context = {
            "tours": tours,
        }

        return render(request, 'cliente/favoritos.html', context)
    else:
        messages.error(request, 'Debes iniciar sesión para ver tus favoritos.')
        return redirect('login')


@ login_required(login_url='login')
def delete_favorite(request, tour_id):
    """
    Author: Leonardo Ortega
    Remove a tour from the user's favorite list.
    Args:
        request (HttpRequest): The HTTP request object containing user information.
        tour_id (int): The ID of the tour to be removed from the favorite list.
    Returns:
        HttpResponseRedirect: Redirects to the 'favorites' page after removing the tour.
    Raises:
        Http404: If the tour with the given ID does not exist.
    Side Effects:
        - Removes the specified tour from the user's favorite list.
        - Saves the updated favorite list.
        - Adds a success message to the request.
    """
    favorite_list = FavoriteList.objects.filter(
        client=request.user.client).first()
    tour = get_object_or_404(Tour, id=tour_id)
    favorite_list.tours.remove(tour)
    favorite_list.save()

    messages.success(request, 'Tour eliminado de favoritos.')

    return redirect('favorites')


@ login_required(login_url='login')
def client_purchases(request):
    """
    Author: Neida Franco
    Handles the client purchases view.
    This view retrieves all reservations made by the logged-in client and the reviews associated with those reservations.
    It then renders the 'cliente/historial.html' template with the retrieved data.
    Args:
        request (HttpRequest): The HTTP request object.
    Returns:
        HttpResponse: The rendered 'cliente/historial.html' template with the context containing the client's reservations and reviews.
    """
    reservaciones = Reservation.objects.filter(client=request.user.client)
    reviews = Reviews.objects.filter(reservation__in=reservaciones)

    context = {
        'reservaciones': reservaciones,
        'reviews': reviews
    }

    return render(request, 'cliente/historial.html', context)


class CreateReview(CreateView):
    """
    Author: Santiago Mendivil
    A view to create a new Review object.

    Attributes:
        model (Review): The model associated with this view.
        form_class (ReviewForm): The form class to be used for creating a review.
        template_name (str): The name of the template to be rendered.
        success_url (str): The URL to redirect to upon successful form submission.
    """
    model = Reviews
    template_name = 'cliente/reseña.html'
    fields = ['rating', 'review_text']
    success_url = reverse_lazy('client_purchases')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        reservation = Reservation.objects.get(id=self.kwargs['reservation_id'])
        tour = reservation.tour
        context['reservation_id'] = reservation.id
        context['agency_name'] = tour.agency
        context['destination_place'] = tour.destination_place
        return context

    def form_valid(self, form):
        form.instance.reservation = Reservation.objects.get(
            id=self.kwargs['reservation_id'])
        return super().form_valid(form)


class DeleteReview(DeleteView):
    """
    Author: Santiago Mendivil
    A view to delete a Review object.

    Attributes:
        model (Review): The model associated with this view.
        template_name (str): The name of the template to be rendered.
        success_url (str): The URL to redirect to upon successful form submission.
    """
    model = Reviews
    template_name = 'cliente/eliminar_reseña.html'
    success_url = reverse_lazy('client_purchases')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['review_id'] = self.kwargs['pk']
        return context

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        return redirect(self.success_url)


@ login_required(login_url='login')
def payment_methods_client(request):
    """
    Author: Hector Ramos
    Handles the request to display the payment methods for a client.
    This view function retrieves the payment methods associated with the 
    currently logged-in client and renders them in the 'metodos_pago.html' 
    template.
    Args:
        request (HttpRequest): The HTTP request object containing metadata 
        about the request.
    Returns:
        HttpResponse: The rendered 'metodos_pago.html' template with the 
        client's payment methods.
    """
    metodos = PaymentMethod.objects.filter(client=request.user.client)

    return render(request, 'cliente/metodos_pago.html', {'metodos': metodos})


@login_required
def add_payment_method(request):
    """
    Author: Hector Ramos
    Handles the addition of a new payment method for the logged-in user.
    This view processes a POST request to attach a new Stripe payment method to the user's Stripe customer account,
    sets it as the default payment method for future invoices, and saves the payment method details in the database.
    Args:
        request (HttpRequest): The HTTP request object containing metadata about the request.
    Returns:
        HttpResponse: Redirects to the 'payment_methods_client' view if the payment method is successfully added.
        Otherwise, renders the 'cliente/agregar_metodo_pago.html' template with the Stripe public key.
    POST Parameters:
        stripe_payment_method_id (str): The ID of the Stripe payment method to be attached.
        cardholder_name (str): The name of the cardholder as provided in the form.
    Template:
        cliente/agregar_metodo_pago.html: The template rendered if the request method is not POST or if the payment method ID is not provided.
    Context:
        stripe_public_key (str): The public key for Stripe, used in the template for client-side Stripe operations.
    """
    if request.method == 'POST':
        stripe_payment_method_id = request.POST.get('stripe_payment_method_id')
        # Obtener el nombre del titular desde el formulario
        cardholder_name = request.POST.get('cardholder_name')

        if stripe_payment_method_id:
            customer_id = request.user.client.stripe_customer_id

            payment_method = stripe.PaymentMethod.attach(
                stripe_payment_method_id,
                customer=customer_id,
            )

            stripe.Customer.modify(
                customer_id,
                invoice_settings={
                    'default_payment_method': stripe_payment_method_id,
                },
            )

            PaymentMethod.objects.create(
                client=request.user.client,
                method_type='credit_card',
                stripe_payment_method_id=stripe_payment_method_id,
                card_last4=payment_method.card.last4,
                card_brand=payment_method.card.brand,
                cardholder_name=cardholder_name,
            )

            return redirect('payment_methods_client')

    return render(request, "cliente/agregar_metodo_pago.html", {'stripe_public_key': settings.STRIPE_PUBLIC_KEY})


@login_required
def set_default_payment_method(request, metodo_id):
    """
    Author: Hector Ramos
    Sets the specified payment method as the default for the current user.
    This function retrieves the payment method specified by `metodo_id` for the
    current user, sets all other payment methods for the user to non-default,
    and then sets the specified payment method as the default.
    Args:
        request (HttpRequest): The HTTP request object containing the current user.
        metodo_id (int): The ID of the payment method to set as default.
    Returns:
        HttpResponseRedirect: A redirect to the 'payment_methods_client' view.
    Raises:
        Http404: If the payment method with the given ID does not exist for the current user.
    """
    metodo = get_object_or_404(
        PaymentMethod, id=metodo_id, client=request.user.client)

    PaymentMethod.objects.filter(
        client=request.user.client).update(is_default=False)

    metodo.is_default = True
    metodo.save()

    return redirect('payment_methods_client')


@login_required
def delete_payment_method(request, metodo_id):
    """
    Author: Hector Ramos, Leonardo Ortega
    Deletes a payment method for the current user.
    Args:
        request (HttpRequest): The HTTP request object containing user information.
        metodo_id (int): The ID of the payment method to be deleted.
    Returns:
        HttpResponse: A redirect to the 'payment_methods_client' view.
    Raises:
        Http404: If the payment method does not exist or does not belong to the current user.
    Notes:
        - If the payment method is the default method, it cannot be deleted and an error message is shown.
        - If the payment method is successfully deleted, a success message is shown.
    """
    metodo = get_object_or_404(
        PaymentMethod, id=metodo_id, client=request.user.client)

    if metodo.is_default:
        messages.error(
            request, "No puedes eliminar el método de pago predeterminado. Por favor, selecciona otro método predeterminado primero.")
    else:
        metodo.delete()
        messages.success(
            request, "El método de pago ha sido eliminado exitosamente.")

    return redirect('payment_methods_client')


@login_required(login_url='login')
def agency_dashboard(request):
    """
    Author: Santiago Mendivil
    Renders the agency dashboard page.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The rendered agency dashboard HTML page.
    """
    return render(request, 'agency_dashboard.html')


@login_required(login_url='login')
def agency_profile(request):
    """
    Author: Santiago Mendivil
    Handle the agency profile view.
    This view allows an agency to update its profile information. If the request
    method is POST, it processes the submitted forms for updating the agency's
    profile and saves the changes if the forms are valid. If the request method
    is GET, it initializes the forms with the current agency's information.
    Args:
        request (HttpRequest): The HTTP request object.
    Returns:
        HttpResponse: The rendered agency profile page with the forms and context data.
    Context:
        agency_form (AgencyForm): The form for updating the agency's basic information.
        agency_profile_form (AgencyProfileForm): The form for updating the agency's profile details.
        agencia (Agency): The agency object associated with the current user.
        valid_states (list): A list of valid states for the agency profile.
    Templates:
        agencia/perfil.html: The template for rendering the agency profile page.
    """
    agencia = get_object_or_404(Agency, user=request.user)

    if request.method == 'POST':
        agency_form = AgencyForm(request.POST, request.FILES, instance=agencia)
        agency_profile_form = AgencyProfileForm(
            request.POST, request.FILES, instance=agencia)

        if agency_form.is_valid() and agency_profile_form.is_valid():
            agency_form.save()
            agency_profile_form.save()
            messages.success(request, 'Tu perfil ha sido actualizado.')
            return redirect('agency_profile')
    else:
        agency_form = AgencyForm(instance=agencia)
        agency_profile_form = AgencyProfileForm(instance=agencia)

    context = {
        'agency_form': agency_form,
        'agency_profile_form': agency_profile_form,
        'agencia': agencia,
        'valid_states': VALID_STATES
    }

    return render(request, 'agencia/perfil.html', context)


@login_required(login_url='login')
def reports(request):
    """
    Author: Neida Franco
    Generates a report view for the tours associated with the agency of the logged-in user.
    This view filters the tours based on the agency of the current user and renders the 
    'agencia/reportes.html' template with the filtered tours.
    Args:
        request (HttpRequest): The HTTP request object containing metadata about the request.
    Returns:
        HttpResponse: The rendered 'agencia/reportes.html' template with the context containing 
                        the filtered tours.

    """
    agency_tours = Tour.objects.filter(agency=request.user.agency)

    context = {
        'tours': agency_tours
    }

    return render(request, 'agencia/reportes.html', context)


@login_required(login_url='login')
def generate_report(request, tour_id):
    """
    Author: Santiago Mendivil
    Generates a PDF report for a specific tour and returns it as an HTTP response.
    Args:
        request (HttpRequest): The HTTP request object.
        tour_id (int): The ID of the tour for which the report is to be generated.
    Returns:
        HttpResponse: An HTTP response with the generated PDF report as its content.
    Raises:
        Http404: If the tour with the given ID does not exist.
    The report includes the following information about the tour:
        - Title
        - Description
        - Lodging place
        - Price per person
        - Capacity
        - Total bookings
        - Start date
        - End date
        - Place of origin
        - Destination place
        - Total clients
        - Total earnings
        - Additional transaction details:
            - Client name
            - Client email
            - Number of people
            - Total price paid
            - Date and time of transaction
    """
    tour = get_object_or_404(Tour, id=tour_id)

    report, created = Reports.objects.get_or_create(
        agency=tour.agency, tour=tour
    )
    report.save()

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer)

    p.setFont("Helvetica-Bold", 16)
    p.drawString(100, 800, f"Reporte del Tour: {tour.title}")

    p.setFont("Helvetica", 12)
    data = [
        ["Descripción", tour.description],
        ["Lugar de hospedaje", tour.lodging_place],
        ["Precio por persona", f"${tour.price_per_person}"],
        ["Capacidad", tour.capacity],
        ["Total de reservas", tour.total_bookings],
        ["Fecha de inicio", tour.start_date.strftime('%d/%m/%Y %H:%M')],
        ["Fecha de fin", tour.end_date.strftime('%d/%m/%Y %H:%M')],
        ["Lugar de origen", tour.place_of_origin],
        ["Lugar de destino", tour.destination_place],
        ["Total de clientes", report.total_clients],
        ["Ganancias totales", f"${report.earnings}"]
    ]

    x = 100
    y = 750
    for row in data:
        if y < 50:  
            p.showPage()
            y = 750
        p.drawString(x, y, row[0])
        p.drawString(x + 200, y, str(row[1]))
        y -= 20

    p.setFont("Helvetica-Bold", 14)
    y -= 30
    p.drawString(100, y, "Detalles de las Transacciones:")
    y -= 20

    transactions = Payments.objects.filter(
        reservation__tour=tour,
        status='completado'
    ).select_related('reservation__client__user' )

    if not transactions:
        if y < 50: 
            p.showPage()
            y = 750
        p.drawString(100, y, "No hay transacciones completadas para este tour.")
    else:
        table_data = [["Nombre", "Correo", "Personas", "Precio Total", "Fecha"]] 
        for transaction in transactions:
            table_data = [["Folio", "Nombre", "Correo", "Personas", "Precio Total", "Fecha y hora"]] 
            for payment in transactions:
                reservation = payment.reservation
                client = reservation.client.user
                full_name = f"{client.first_name} {client.last_name}"
                table_data.append([
                    f"#{reservation.folio}",
                    full_name,
                    client.email,
                    reservation.number_people,
                    f"${payment.amount}",
                    payment.payment_date.strftime('%d/%m/%Y %H:%M')
                ])

        table = Table(table_data, colWidths=[60, 80, 150, 50, 80, 100])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))

        table_height = 20 * len(table_data)  
        if y - table_height < 50:  
            p.showPage()
            y = 750

        table.wrapOn(p, 50, y)
        table.drawOn(p, 50, y - table_height)

    p.save()
    buffer.seek(0)
    return HttpResponse(buffer, content_type='application/pdf')



@login_required(login_url='login')
def tours_dashboard(request):
    """
    Author: Neida Franco
    Renders the tours dashboard page.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The rendered tours dashboard HTML page.
    """
    tours = Tour.objects.filter(agency=request.user.agency)

    context = {
        'tours': tours,
    }

    return render(request, 'agencia/tours_dashboard.html', context)


class CreateTour(CreateView):

    """
    A view to create a new Tour object. This view handles the creation of a new Tour object, including form validation
    to ensure that the start date is before the end date and that both dates are in the future.

    Attributes:
        model (Tour): The model associated with this view.
        fields (list): The fields to be displayed in the form.
        template_name (str): The name of the template to be rendered.
        success_url (str): The URL to redirect to upon successful form submission.

    Methods:
        dispatch():
            Checks if the agency has at least one payment method before allowing access to the view.
            Redirects to the payment method creation page if no payment method is found.
        form_valid(form):
            Validates the form data, ensuring that the start date is before the end date
            and that both dates are in the future. Adds errors to the form if validation fails.
            Sets the total bookings to 0 and assigns the agency to the current user.
            Returns the result of the parent class's form_valid method if validation passes.

    """
    model = Tour
    fields = ['title', 'description', 'lodging_place', 'price_per_person', 'capacity',
                'start_date', 'end_date', 'place_of_origin', 'destination_place', 'tour_image']
    template_name = 'agencia/crear_tour.html'
    success_url = reverse_lazy('tours_dashboard')

    def dispatch(self, request, *args, **kwargs):
        if not PaymentMethod.objects.filter(agency=request.user.agency).exists():
            messages.error(request, "Debes agregar un método de pago antes de poder crear un tour.")
            return redirect(reverse('payment_methods_agency'))

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        start_date = form.cleaned_data.get('start_date')
        end_date = form.cleaned_data.get('end_date')

        if start_date >= end_date:
            form.add_error(
                'start_date', 'La fecha de inicio debe ser anterior a la fecha de fin.')
            return self.form_invalid(form)

        if start_date < timezone.now():
            form.add_error(
                'start_date', 'La fecha de inicio debe ser posterior a la fecha actual.')
            return self.form_invalid(form)

        if end_date < timezone.now():
            form.add_error(
                'end_date', 'La fecha de fin debe ser posterior a la fecha actual.')
            return self.form_invalid(form)

        form.instance.total_bookings = 0
        form.instance.agency = self.request.user.agency
        return super().form_valid(form)


def payment_methods_agency(request):
    """
    Author: Hector Ramos
    Handles the request to display payment methods for the agency associated with the current user.
    Args:
        request (HttpRequest): The HTTP request object containing metadata about the request.
    Returns:
        HttpResponse: The rendered HTML page displaying the payment methods for the agency.
    """
    metodos = PaymentMethod.objects.filter(agency=request.user.agency)

    # Generar el enlace del dashboard de Stripe a partir del account ID de Stripe
    stripe_agency_id = request.user.agency.stripe_agency_id if hasattr(request.user.agency, 'stripe_agency_id') else None
    stripe_dashboard_link = f"https://dashboard.stripe.com/{stripe_agency_id}/overview" if stripe_agency_id else None

    return render(request, 'agencia/metodos_pago.html', {
        'metodos': metodos,
        'stripe_dashboard_link': stripe_dashboard_link
    })



def add_payment_methods_agency(request):
    """
    Author: Hector Ramos
    Handles the request to display payment methods for the agency associated with the current user.
    Args:
        request (HttpRequest): The HTTP request object containing metadata about the request.
    Returns:
        HttpResponse: The rendered HTML page displaying the payment methods for the agency.
    """
    if request.method == 'POST':
        transfer_number = request.POST.get('transfer_number')
        if transfer_number:
            if PaymentMethod.objects.filter(agency=request.user.agency, transfer_number=transfer_number).exists():
                messages.error(request, "Este número de transferencia ya está registrado.")
            else:
                try:
                    PaymentMethod.objects.create(agency=request.user.agency, transfer_number=transfer_number)
                    messages.success(request, "Método de pago agregado exitosamente.")
                except IntegrityError:
                    messages.error(request, "Error al guardar el método de pago.")
            return redirect('payment_methods_agency')
        else:
            messages.error(request, "Por favor, ingresa un número de transferencia válido.")

    metodos = PaymentMethod.objects.filter(agency=request.user.agency)
    return render(request, 'agencia/agregar_metodos_pago.html', {'metodos': metodos})

def delete_payment_method(request, metodo_id):
    """
    Handles the request to delete a specific payment method for the agency.
    Args:
        request (HttpRequest): The HTTP request object.
        metodo_id (int): The ID of the payment method to delete.
    Returns:
        HttpResponse: Redirects to the payment methods page with a success or error message.
    """
    metodo = get_object_or_404(PaymentMethod, id=metodo_id, agency=request.user.agency)
    
    metodo.delete()
    messages.success(request, "Método de pago eliminado exitosamente.")
    return redirect('payment_methods_agency')
