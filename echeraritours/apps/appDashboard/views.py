from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from apps.appUser.models import Client, Agency
from apps.appPayment.models import PaymentMethod
from apps.appTour.models import Reservation
from django.views.generic.edit import CreateView

# Create your views here.


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
    cliente = Client.objects.get(user=request.user)

    return render(request, 'cliente/perfil.html', {'cliente': cliente})


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
