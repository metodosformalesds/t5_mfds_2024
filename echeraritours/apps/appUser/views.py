import time
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from echeraritours import settings
from django.core.files.storage import default_storage
import requests
import boto3
import idanalyzer
import io
import base64
import qrcode

# Para los formularios
from django.contrib.auth.forms import UserCreationForm
from .forms import CreateUserForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from allauth.socialaccount.models import SocialAccount
from datetime import datetime, timedelta


# Para los decoradores que validan ciertas vistas
from .decorators import unauthenticated_user
from django.contrib.auth.decorators import login_required

# Para modelos
from .models import Client, Agency
from apps.appTour.models import Reviews, Tour
from django.core.files.storage import FileSystemStorage

# Para recuperacion de contraseña
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.models import User
import threading
from django.core.mail import send_mail
from .models import User
from django.contrib.auth.views import PasswordResetConfirmView
from django.urls import reverse_lazy
import random


# Create your views here.


def index(request):
    """
    Author: Leonardo Ortega 
    View function for the index page of the appUser application.
    This function retrieves the latest 5 reviews from the Reviews model,
    ordered by the review date in descending order, and renders the 'index.html'
    template with the retrieved reviews.
    Args:
        request (HttpRequest): The HTTP request object.
    Returns:
        HttpResponse: The rendered 'index.html' template with the context containing
                        the latest 5 reviews.
    """
    reviews = Reviews.objects.order_by('-review_date')[:3]
    tours = Tour.objects.all()

    return render(request, 'index.html', {'reviews': reviews, 'tours': tours})


def registerPage(request):
    """
    Author: Santiago Mendivil
    Handles the user registration process.
    If the user is authenticated and has a linked Google account, pre-fills the registration form with the user's Google email.
    If the request method is POST, validates and saves the registration form, creates a new user, and redirects to the login page.
    Args:
        request (HttpRequest): The HTTP request object.
    Returns:
        HttpResponse: The rendered registration page with the registration form.
    """
    email = ''
    if request.user.is_authenticated:
        try:
            google_account = SocialAccount.objects.get(
                provider='google', user=request.user)
            email = google_account.extra_data.get('email', '')
        except SocialAccount.DoesNotExist:
            pass
    form = CreateUserForm(initial={'email': email})

    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()

            user = form.cleaned_data.get('username')
            messages.success(request, f"Usuario creado para {user}")

            return redirect('login')

    context = {'form': form}
    return render(request, 'register.html', context)


def loginPage(request):
    """
    Author: Santiago Mendivil
    Handles the user login functionality.
    This view processes the login form submission. If the request method is POST,
    it retrieves the email and password from the request, authenticates the user,
    and logs them in if the credentials are correct. If the credentials are incorrect,
    it displays an error message. If the request method is not POST, it simply renders
    the login page.
    Args:
        request (HttpRequest): The HTTP request object containing metadata about the request.
    Returns:
        HttpResponse: Redirects to 'seleccion_registro' if login is successful, otherwise
                      renders the login page with an error message.
    """
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            return redirect('seleccion_registro')
        else:
            messages.info(request, 'El correo o contraseña son incorrectos')

    context = {}
    return render(request, 'login.html', context)


def logoutUser(request):
    """
    Author: Hector Ramos
    Logs out the current user and redirects them to the login page.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponseRedirect: A redirect to the login page.
    """
    logout(request)
    return redirect('login')


@login_required
def registrar_cliente(request):
    """
    Author: Santiago Mendivil
    Handles the multi-step client registration process.
    This view manages a three-step form submission process for registering a client.
    The steps are managed using the session to keep track of the current step.
    Steps:
        1. Collects first name, paternal surname, maternal surname, and birth date.
        2. Collects phone number, zip code, and city.
        3. Uploads and saves an official identification file and a biometric image.
        4. Calls the api of ID Analyzer to validate the identification and biometric images.
    Args:
        request (HttpRequest): The HTTP request object.
    Returns:
        HttpResponse: Renders the 'registrar_cliente.html' template with the current step.
        HttpResponse: Redirects to 'registrar_cliente' to proceed to the next step.
        HttpResponse: Redirects to 'index' upon successful registration.
        HttpResponse: Returns an error message if required fields are missing or an error occurs.
    """
    if 'form_step' not in request.session:
        request.session['form_step'] = 1

    if request.method == 'POST':

        if 'previous' in request.POST:
            if request.session['form_step'] > 1:
                request.session['form_step'] -= 1
            return redirect('registrar_cliente')

        if request.session['form_step'] == 1:
            first_name = request.POST.get('nombre')
            paternal_surname = request.POST.get('apellido_paterno')
            maternal_surname = request.POST.get('apellido_materno')
            birth_date = request.POST.get('fecha_nacimiento')

            if first_name and paternal_surname and maternal_surname and birth_date:
                birth_date = datetime.strptime(birth_date, '%Y-%m-%d')
                today = datetime.now()
                age = today.year - birth_date.year - \
                    ((today.month, today.day) < (birth_date.month, birth_date.day))

                if age < 18:
                    messages.error(
                        request, 'Debes ser mayor de edad para registrarte.')
                    return redirect('registrar_cliente')
                elif age > 100:
                    messages.error(
                        request, 'Por favor ingresa una fecha de nacimiento válida.')
                    return redirect('registrar_cliente')

                birth_date = request.POST.get('fecha_nacimiento')

                request.session['first_name'] = first_name
                request.session['paternal_surname'] = paternal_surname
                request.session['maternal_surname'] = maternal_surname
                request.session['birth_date'] = birth_date

                request.session['form_step'] = 2
                return redirect('registrar_cliente')
            else:
                return HttpResponse('Por favor completa todos los campos.')

        elif request.session['form_step'] == 2:
            phone = request.POST.get('telefono')
            zip_code = request.POST.get('codigo-postal')
            city = request.POST.get('ciudad')

            if phone and zip_code and city:
                request.session['phone'] = phone
                request.session['zip_code'] = zip_code
                request.session['city'] = city

                request.session['form_step'] = 3
                return redirect('registrar_cliente')
            else:
                return HttpResponse('Por favor completa todos los campos.')

        elif request.session['form_step'] == 3 and 'identificacion_oficial' in request.FILES and 'identificacion_biometrica' in request.FILES:
            id_identificacion_oficial = request.FILES['identificacion_oficial']
            id_identificacion_biometrica = request.FILES['identificacion_biometrica']

            s3 = boto3.client('s3',
                              aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                              aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                              region_name=settings.AWS_S3_REGION_NAME)

            official_id_key = f"uploads/{id_identificacion_oficial.name}"
            biometric_id_key = f"uploads/{id_identificacion_biometrica}_biometric.jpg"

            s3.upload_fileobj(id_identificacion_oficial,
                              settings.AWS_STORAGE_BUCKET_NAME, official_id_key)
            s3.upload_fileobj(id_identificacion_biometrica,
                              settings.AWS_STORAGE_BUCKET_NAME, biometric_id_key)

            # URLs completas de los archivos en S3 utilizando el dominio personalizado y las rutas de cada archivo
            # official_id_url = f"https://{settings.AWS_S3_CUSTOM_DOMAIN}/{official_id_key}"
            # biometric_id_url = f"https://{settings.AWS_S3_CUSTOM_DOMAIN}/{biometric_id_key}"
            official_id_url = s3.generate_presigned_url('get_object',
                                                        Params={
                                                            'Bucket': settings.AWS_STORAGE_BUCKET_NAME, 'Key': official_id_key},
                                                        ExpiresIn=3600)
            biometric_id_url = s3.generate_presigned_url('get_object',
                                                         Params={
                                                             'Bucket': settings.AWS_STORAGE_BUCKET_NAME, 'Key': biometric_id_key},
                                                         ExpiresIn=3600)

            try:
                client = idanalyzer.CoreAPI(
                    f"{settings.ID_ANALYZER_API_KEY}", 'US')

                client.throw_api_exception(True)

                # Llamada a la API de ID Analyzer
                response = client.scan(
                    document_primary=official_id_url,
                    biometric_photo=biometric_id_url
                )
                print(response)

                # Procesa la respuesta de ID Analyzer
                if response.get('verification', {}).get('passed'):
                    client, created = Client.objects.update_or_create(
                        user=request.user,
                        defaults={
                            'first_name': request.session['first_name'],
                            'paternal_surname': request.session['paternal_surname'],
                            'maternal_surname': request.session['maternal_surname'],
                            'birth_date': request.session['birth_date'],
                            'phone': request.session['phone'],
                            'zip_code': request.session['zip_code'],
                            'city': request.session['city'],
                            'id_identificacion_oficial_url': official_id_url,
                            'id_identificacion_biometrica_url': biometric_id_url,
                        }
                    )

                    if created:
                        for key in ['first_name', 'paternal_surname', 'maternal_surname', 'birth_date', 'phone', 'zip_code', 'city', 'form_step']:
                            if key in request.session:
                                del request.session[key]

                        return redirect('index')
                    else:
                        return HttpResponse('El cliente ya está registrado o ocurrió un error al ser guardado.')
                else:
                    messages.info(
                        request, 'No pudimos validar las fotos que proporcionaste, intentalo de nuevo')
            except idanalyzer.APIError as e:
                details = e.args[0]
                print(
                    f"API error code {details['code']}, message: {details['message']}")

        else:
            return HttpResponse('Debe dar una identificación válida y una imagen biométrica.')

    step = request.session['form_step']

    return render(request, 'registrar_cliente.html', {'step': step})


@login_required
def registrar_agencia(request):
    """
    Author: Santiago Mendivil
    View for registering an authenticated user as an Agency.
    This view handles a multi-step form for agency registration. The form has two steps:
    1. Collecting basic agency information (name, address, phone, zip code).
    2. Uploading a certificate file.
    The form step is tracked using the session variable 'form_step'.
    Args:
        request (HttpRequest): The HTTP request object.
    Returns:
        HttpResponse: Redirects to the same view to handle form steps or to the index page upon successful registration.
        Renders the 'registrar_agencia.html' template with the current form step.
    """

    if 'form_step' not in request.session:
        request.session['form_step'] = 1

    if request.method == 'POST':

        if 'previous' in request.POST:
            if request.session['form_step'] > 1:
                request.session['form_step'] -= 1
            return redirect('registrar_agencia')

        if request.session['form_step'] == 1:
            agency_name = request.POST.get('nombre-agencia')
            state = request.POST.get('estado')
            phone = request.POST.get('telefono')
            zip_code = request.POST.get('codigo-postal')

            if agency_name and state and phone and zip_code:
                request.session['agency_name'] = agency_name
                request.session['state'] = state
                request.session['phone'] = phone
                request.session['zip_code'] = zip_code

                request.session['form_step'] = 2
                return redirect('registrar_agencia')
            else:
                return HttpResponse('Por favor completa todos los campos.')

        elif request.session['form_step'] == 2:
            # Esta es la calle a partir de ahora
            address = request.POST.get('direccion')
            suburb = request.POST.get('colonia')
            town = request.POST.get('municipio')

            if address and suburb and town:
                request.session['address'] = address
                request.session['suburb'] = suburb
                request.session['town'] = town
            else:
                return HttpResponse('Por favor completa todos los campos.')

            agency, created = Agency.objects.update_or_create(
                user=request.user,
                defaults={
                    'agency_name': request.session['agency_name'],
                    'state': request.session['state'],
                    'address': request.session['address'],
                    'suburb': request.session['suburb'],
                    'town': request.session['town'],
                    'phone': request.session['phone'],
                    'zip_code': request.session['zip_code'],
                }
            )

            if created:
                for key in ['agency_name', 'address', 'suburb', 'town', 'phone', 'zip_code', 'form_step']:
                    del request.session[key]

                return redirect('index')
            else:
                return HttpResponse('La agencia ya esta registrada u ocurrio un error al ser guardado.')

        else:
            return HttpResponse('Ingresa campos validos.')

    step = request.session['form_step']
    return render(request, 'registrar_agencia.html', {'step': step})


@login_required(login_url='login')
def seleccion_registro(request):
    """
    Author: Leonardo Ortega
    Renders the selection page. If the user is already part of a user type (Client or Agency), redirects to the main page.
    Args:
        request (HttpRequest): The HTTP request object.
    Returns:
        HttpResponse: The rendered selection page or a redirect to the main page if the user is already a Client or Agency.
    """
    if Client.objects.filter(user=request.user).exists() or Agency.objects.filter(user=request.user).exists():
        return redirect('index')

    return render(request, 'seleccion_registro.html')


def sobre_nosotros(request):
    """
    Author: Neida Franco
    Handles the HTTP request for the 'Sobre Nosotros' (About Us) page.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The rendered 'sobre_nosotros.html' template.
    """
    return render(request, 'sobre_nosotros.html')


def terminos_y_condiciones(request):
    """
    Author: Neida Franco
    Handles the request to display the terms and conditions page.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The rendered terms and conditions HTML page.
    """
    return render(request, 'terminos_y_condiciones.html')


def terminos_y_condiciones2(request):
    """
    Author: Neida Franco
    Renders the 'terminos_y_condiciones2.html' template.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The rendered 'terminos_y_condiciones2.html' template.
    """
    return render(request, 'terminos_y_condiciones2.html')


def terminos_legales(request):
    """
    Author: Neida Franco
    Handles the HTTP request for the 'terminos_legales' page.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The rendered 'terminos_legales.html' template.
    """
    return render(request, 'terminos_legales.html')


def necesitas_ayuda(request):
    """
    Author: Neida Franco
    Handles the request to render the 'necesitas_ayuda.html' template.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The rendered 'necesitas_ayuda.html' template.
    """
    return render(request, 'necesitas_ayuda.html')


def solicitar_correo(request):
    if request.method == 'POST':
        email = request.POST.get('email')

        try:
            usuario = User.objects.filter(email=email).first()
            codigo = generar_codigo()

            if hasattr(usuario, 'client'):
                usuario.client.codigo_recuperacion = codigo
                usuario.client.save()
            elif hasattr(usuario, 'agency'):
                usuario.agency.codigo_recuperacion = codigo
                usuario.agency.save()
            else:
                messages.error(
                    request, 'El usuario no tiene un perfil válido.')
                return redirect('solicitar_correo')

            request.session['email'] = email
            request.session['codigo'] = codigo

            send_mail(
                'Código de recuperación',
                f'Tu código de recuperación es: {codigo}',
                'echeraritours@gmail.com',
                [email],
                fail_silently=False,
            )
            messages.success(
                request, 'El código de recuperación ha sido enviado.')
            return redirect('verificar_codigo')
        except User.DoesNotExist:
            messages.error(
                request, 'El correo no está asociado a ninguna cuenta.')
    return render(request, 'solicitar_correo.html')


def generar_codigo():
    return random.randint(100000, 999999)


def verificar_codigo(request):
    email = request.session.get('email')

    if request.method == 'POST':

        codigo = ''.join([
            request.POST.get(f'codigo_{i}', '') for i in range(1, 7)
        ])

        try:
            usuario = User.objects.get(email=email)
            if hasattr(usuario, 'client') and str(usuario.client.codigo_recuperacion) == codigo:
                request.session['email'] = email
                return redirect('restablecer_contrasena')
            elif hasattr(usuario, 'agency') and str(usuario.agency.codigo_recuperacion) == codigo:
                request.session['email'] = email
                return redirect('restablecer_contrasena')
            else:
                messages.error(request, 'El código ingresado es incorrecto.')
        except User.DoesNotExist:
            messages.error(
                request, 'El correo no está asociado a ninguna cuenta.')
    return render(request, 'verificar_codigo.html', {'email': email})


def restablecer_contrasena(request):
    if request.method == 'POST':
        nueva_password = request.POST.get('password')
        confirmar_password = request.POST.get('confirm_password')

        if nueva_password != confirmar_password:
            messages.error(request, 'Las contraseñas no coinciden.')
            return redirect('restablecer_contrasena')

        email = request.session.get('email')
        if not email:
            messages.error(request, 'Ocurrió un error, intenta nuevamente.')
            return redirect('verificar_codigo')

        try:
            usuario = User.objects.get(email=email)

            usuario.set_password(nueva_password)
            usuario.save()

            if hasattr(usuario, 'client'):
                usuario.client.codigo_recuperacion = None
                usuario.client.save()
            elif hasattr(usuario, 'agency'):
                usuario.agency.codigo_recuperacion = None
                usuario.agency.save()

            messages.success(
                request, 'Tu contraseña ha sido restablecida con éxito.')
            return redirect('login')
        except User.DoesNotExist:
            messages.error(
                request, 'El correo no está asociado a ninguna cuenta.')
            return redirect('verificar_codigo')

    return render(request, 'restablecer_contrasena.html')


def google_login(request):
    """
    Author: Neida Franco 
    Handles Google login for users.
    If the user is already authenticated, they are redirected to the index page.
    If the user is not authenticated, the function checks if there is a social account associated with the user.
    If a social account is found, it retrieves the email from the social account's extra data.
    If a user with the retrieved email exists, the user is logged in and redirected to the index page.
    If no user with the retrieved email exists, a new user is created with the email, a username derived from the email,
    and a random password. The new user is then logged in and redirected to the profile setup page.
    If no social account is found, the user is redirected to the login page.
    Args:
        request (HttpRequest): The HTTP request object.
    Returns:
        HttpResponse: A redirect to the appropriate page based on the user's authentication status and social account existence.
    """
    if request.user.is_authenticated:
        return redirect('index')

    social_account = SocialAccount.objects.filter(user=request.user).first()
    if social_account:
        email = social_account.extra_data.get('email')
        if User.objects.filter(email=email).exists():
            user = authenticate(request, email=email)
            login(request, user)
            return redirect('index')
        else:
            return redirect('register', email=email)

    return redirect('index')
