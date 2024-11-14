import io
from django.conf import settings
from reportlab.pdfgen import canvas
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

from django.views.generic.edit import CreateView
from .forms import UserForm, UserProfileForm, AgencyForm, AgencyProfileForm
from django.contrib import messages

from django.urls import reverse_lazy

# Modelos
from .models import Reports
from apps.appUser.models import Client, Agency
from apps.appPayment.models import PaymentMethod
from apps.appTour.models import Reservation, Tour

# Configurar Stripe
import stripe
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
    Renders the client dashboard page.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The rendered client dashboard HTML page.
    """
    return render(request, 'client_dashboard.html')


def client_active_plans(request):
    reservaciones = Reservation.objects.filter(client=request.user.client)

    return render(request, 'cliente/planes_activos.html', {'reservaciones': reservaciones})


def client_profile(request):
    cliente = get_object_or_404(Client, user=request.user)

    if request.method == 'POST':
        user_form = UserForm(request.POST, request.FILES, instance=cliente)
        profile_form = UserProfileForm(
            request.POST, request.FILES, instance=cliente)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Tu perfil ha sido actualizado.')
            return redirect('client_profile')
    else:
        user_form = UserForm(instance=cliente)
        profile_form = UserProfileForm(instance=cliente)

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'cliente': cliente,
        'valid_states': VALID_STATES
    }

    return render(request, 'cliente/perfil.html', context)


@login_required
def payment_methods_client(request):
    metodos = PaymentMethod.objects.filter(client=request.user.client)
    context = {
        'metodos': metodos,
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY 
    }
    return render(request, 'cliente/metodos_pago.html', context)

@login_required
def add_payment_method(request):
    if request.method == 'POST':
        stripe_payment_method_id = request.POST.get('stripe_payment_method_id')
        
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
                cardholder_name=request.POST.get('cardholder_name')
            )
            return redirect('payment_methods_client')
    
    return render(request, "cliente/agregar_metodo_pago.html", {'stripe_public_key': settings.STRIPE_PUBLIC_KEY})


@login_required
def set_default_payment_method(request, metodo_id):
    metodo = get_object_or_404(PaymentMethod, id=metodo_id, client=request.user.client)
    
    PaymentMethod.objects.filter(client=request.user.client).update(is_default=False)
    
    metodo.is_default = True
    metodo.save()
    
    return redirect('payment_methods_client')

@login_required
def delete_payment_method(request, metodo_id):
    metodo = get_object_or_404(PaymentMethod, id=metodo_id, client=request.user.client)

    if metodo.is_default:
        messages.error(request, "No puedes eliminar el método de pago predeterminado. Por favor, selecciona otro método predeterminado primero.")
    else:
        metodo.delete()
        messages.success(request, "El método de pago ha sido eliminado exitosamente.")

    return redirect('payment_methods_client')



@login_required(login_url='login')
def agency_dashboard(request):
    """
    Renders the agency dashboard page.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The rendered agency dashboard HTML page.
    """
    return render(request, 'agency_dashboard.html')


@login_required(login_url='login')
def agency_profile(request):
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
    agency_tours = Tour.objects.filter(agency=request.user.agency)

    context = {
        'tours': agency_tours
    }

    return render(request, 'agencia/reportes.html', context)


@login_required(login_url='login')
def generate_report(request, tour_id):
    tour = get_object_or_404(Tour, id=tour_id)

    report, created = Reports.objects.get_or_create(
        agency=tour.agency, tour=tour)
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
        p.drawString(x, y, row[0])
        p.drawString(x + 200, y, str(row[1]))
        y -= 20

    p.showPage()
    p.save()
    buffer.seek(0)
    return HttpResponse(buffer, content_type='application/pdf')


@login_required(login_url='login')
def tours_dashboard(request):
    """
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
    A view to create a new Tour object.

    Attributes:
        model (Tour): The model associated with this view.
        fields (list): The fields to be displayed in the form.
        template_name (str): The name of the template to be rendered.
        success_url (str): The URL to redirect to upon successful form submission.
    """
    model = Tour
    fields = ['title', 'description', 'lodging_place', 'price_per_person', 'capacity',
                'start_date', 'end_date', 'place_of_origin', 'destination_place', 'tour_image']
    template_name = 'agencia/crear_tour.html'
    success_url = reverse_lazy('tours_dashboard')

    def form_valid(self, form):
        form.instance.total_bookings = 0
        form.instance.agency = self.request.user.agency
        return super().form_valid(form)


def payment_methods_agency(request):
    metodos = PaymentMethod.objects.filter(agency=request.user.agency)

    return render(request, 'agencia/metodos_pago.html', {'metodos': metodos})
