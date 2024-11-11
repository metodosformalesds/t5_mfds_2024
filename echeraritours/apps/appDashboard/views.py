from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from apps.appUser.models import Client, Agency
from apps.appPayment.models import PaymentMethod
from apps.appTour.models import Reservation, Tour
from django.views.generic.edit import CreateView
from .forms import UserForm, UserProfileForm
from django.contrib import messages
from .models import Reports
from django.urls import reverse_lazy

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


def reports(request):
    agency_tours = Tour.objects.filter(agency=request.user.agency)

    context = {
        'tours': agency_tours
    }

    return render(request, 'agencia/reportes.html', context)


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


# import pandas as pd
# from django.http import HttpResponse
# from reportlab.lib.pagesizes import letter
# from reportlab.pdfgen import canvas
# from .models import Reports

# def export_report(request):
#     if request.method == 'POST':
#         tour_id = request.POST.get('tour_id')
#         agency_id = request.POST.get('agency_id')
#         export_format = request.POST.get('format')
#         tour = Tour.objects.get(id=tour_id)
#         agency = Agency.objects.get(id=agency_id)

#         report = Reports(
#             agency=agency,
#             tour=tour
#         )
#         report.save()

#         if export_format == 'csv':
#             return export_report_csv(report)
#         elif export_format == 'excel':
#             return export_report_excel(report)
#         elif export_format == 'pdf':
#             return export_report_pdf(report)

#     return HttpResponse('Error al generar el reporte.')

# def export_report_csv(report):
#     data = {
#         'Tour Title': [report.tour_title],
#         'Total Clients': [report.total_clients],
#         'Tour Description': [report.tour_description],
#         'Earnings': [report.earnings]
#     }
#     df = pd.DataFrame(data)
#     response = HttpResponse(content_type='text/csv')
#     response['Content-Disposition'] = f'attachment; filename="reporte_{report.tour_title}.csv"'
#     df.to_csv(path_or_buf=response, index=False)
#     return response

# def export_report_excel(report):
#     data = {
#         'Tour Title': [report.tour_title],
#         'Total Clients': [report.total_clients],
#         'Tour Description': [report.tour_description],
#         'Earnings': [report.earnings]
#     }
#     df = pd.DataFrame(data)
#     response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
#     response['Content-Disposition'] = f'attachment; filename="reporte_{report.tour_title}.xlsx"'
#     df.to_excel(response, index=False)
#     return response

# def export_report_pdf(report):
#     response = HttpResponse(content_type='application/pdf')
#     response['Content-Disposition'] = f'attachment; filename="reporte_{report.tour_title}.pdf"'
#     buffer = canvas.Canvas(response, pagesize=letter)
#     buffer.drawString(100, 750, f"Tour Title: {report.tour_title}")
#     buffer.drawString(100, 730, f"Total Clients: {report.total_clients}")
#     buffer.drawString(100, 710, f"Tour Description: {report.tour_description}")
#     buffer.drawString(100, 690, f"Earnings: {report.earnings}")
#     buffer.showPage()
#     buffer.save()
#     return response
