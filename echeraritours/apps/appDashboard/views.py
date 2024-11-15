import io
from reportlab.pdfgen import canvas
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from apps.appUser.models import Client, Agency
from apps.appPayment.models import PaymentMethod
from apps.appTour.models import Reservation, Tour
from django.views.generic.edit import CreateView
from .forms import UserForm, UserProfileForm, AgencyForm, AgencyProfileForm
from django.contrib import messages
from .models import Reports
from django.urls import reverse_lazy
import os
from echeraritours import settings
from .models import FavoriteList

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


@login_required(login_url='login')
def client_active_plans(request):
    reservaciones = Reservation.objects.filter(client=request.user.client)

    return render(request, 'cliente/planes_activos.html', {'reservaciones': reservaciones})


@login_required(login_url='login')
def client_profile(request):
    cliente = get_object_or_404(Client, user=request.user)

    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=cliente)
        profile_form = UserProfileForm(request.POST, request.FILES)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()

            # Si se sube una nueva imagen de perfil
            profile_image = request.FILES.get('profile_image')
            if profile_image:
                # Define la ruta de guardado en static/img/perfil
                save_path = os.path.join(
                    settings.BASE_DIR, 'static', 'img', 'perfil', profile_image.name)

                # Guarda la imagen en static/img/perfil
                with open(save_path, 'wb+') as destination:
                    for chunk in profile_image.chunks():
                        destination.write(chunk)

                cliente.profile_image = 'img/default_profile.jpg'
                profile_form.save()
                cliente.save()
                messages.success(request, 'Perfil actualizado exitosamente.')

            return redirect('client_profile')

    else:
        user_form = UserForm(instance=cliente)
        profile_form = UserProfileForm()

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'cliente': cliente,
    }
    return render(request, 'cliente/perfil.html', context)


@login_required(login_url='login')
def favorites(request):
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


def delete_favorite(request, tour_id):
    favorite_list = FavoriteList.objects.filter(
        client=request.user.client).first()
    tour = get_object_or_404(Tour, id=tour_id)
    favorite_list.tours.remove(tour)
    favorite_list.save()

    messages.success(request, 'Tour eliminado de favoritos.')

    return redirect('favorites')


@login_required(login_url='login')
def payment_methods_client(request):
    metodos = PaymentMethod.objects.filter(client=request.user.client)

    return render(request, 'cliente/metodos_pago.html', {'metodos': metodos})


def add_payment_method(request):
    if request.method == 'POST':
        if request.POST.get('tipo_tarjeta') == 'Tarjeta de crédito' or request.POST.get('tipo_tarjeta') == 'Tarjeta de débito':
            metodo = PaymentMethod(
                client=request.user.client,
                method_type='credit_card',
                stripe_payment_method_id=request.POST.get(
                    'stripe_payment_method_id')
            )
            metodo.save()

    return render(request, "cliente/agregar_metodo_pago.html")


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
