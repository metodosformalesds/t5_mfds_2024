from django.shortcuts import render, redirect
from django.http import HttpResponse

# Para los formularios
from django.contrib.auth.forms import UserCreationForm
from .forms import CreateUserForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout

# Para los decoradores que validan ciertas vistas
from .decorators import unauthenticated_user
from django.contrib.auth.decorators import login_required

# Para modelos
from .models import Client, Agency
from django.core.files.storage import FileSystemStorage

# Create your views here.


def index(request):
    """Renderiza la pagina de inicio de la pagina web

    Args:
        request (HttpRequest): Objeto HttpRequest que contiene los datos de la solicitud

    Returns:
        HttpResponse: Respuesta que renderiza la plantilla 'index.html'
    """

    return render(request, 'index.html')


def registerPage(request):
    """Renderiza la pagina de registro de usuario y procesa el formulario de registro.

    Args:
        request (HttpRequest): Objeto HttpRequest que contiene la informacion del usuario a registrar

    Returns:
        HttpResponse: Creacion de usuario en caso de validar el formulario y redireccion a seleccion
        de registro de tipo de usuario.
    """

    form = CreateUserForm()

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
    """Renderiza la pagina de inicio de sesion y procesa el formulario para iniciar sesion con su usuario
        y contraseña

    Args:
        request (HttpRequest): Objeto HttpRequest que tiene las credenciales del usuario para iniciar sesion

    Returns:
        HttpResponse: Inicio de sesion validado con la informacion recibida.
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
    """Procesa el hecho de cerrar sesion de forma directa del usuario logeado.

    Args:
        request (HttpRequest): Recibe un objeto HttpRequest con la informacion del usuario logeado

    Returns:
        HttpResponse: Se cierra la sesion del usuario con la funcion logout de django.contrib.auth
    """
    logout(request)
    return redirect('login')


@login_required
def registerClient(request):
    """Vista para el registro de un usuario autenticado para ser Cliente"""

    if 'form_step' not in request.session:
        request.session['form_step'] = 1

    if request.method == 'POST':

        if 'previous' in request.POST:
            if request.session['form_step'] > 1:
                request.session['form_step'] -= 1
            return redirect('register_client')

        if request.session['form_step'] == 1:
            first_name = request.POST.get('nombre')
            paternal_surname = request.POST.get('apellido_paterno')
            maternal_surname = request.POST.get('apellido_materno')
            birth_date = request.POST.get('fecha_nacimiento')

            if first_name and paternal_surname and maternal_surname and birth_date:
                request.session['first_name'] = first_name
                request.session['paternal_surname'] = paternal_surname
                request.session['maternal_surname'] = maternal_surname
                request.session['birth_date'] = birth_date

                request.session['form_step'] = 2
                return redirect('register_client')
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
                return redirect('register_client')
            else:
                return HttpResponse('Por favor completa todos los campos.')

        elif request.session['form_step'] == 3 and 'identificacion_oficial' in request.FILES:
            identification = request.FILES['identificacion_oficial']
            fs = FileSystemStorage(location='static/identifications/')
            filename = fs.save(identification.name, identification)
            uploaded_file_url = fs.url(filename)

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
                    'identification': uploaded_file_url,
                }
            )

            if created:
                for key in ['first_name', 'paternal_surname', 'maternal_surname', 'birth_date', 'phone', 'zip_code', 'city', 'form_step']:
                    if key in request.session:
                        del request.session[key]

                return redirect('index')
            else:
                return HttpResponse('El cliente ya esta registrado o ocurrio un error al ser guardado')

        else:
            return HttpResponse('Debe dar una identificacion valida.')

    step = request.session['form_step']

    return render(request, 'register_client.html', {'step': step})


@login_required
def registerAgency(request):
    """Vista para el registro de un usuario autenticado para ser Agencia"""

    if 'form_step' not in request.session:
        request.session['form_step'] = 1

    if request.method == 'POST':

        if 'previous' in request.POST:
            if request.session['form_step'] > 1:
                request.session['form_step'] -= 1
            return redirect('register_agency')

        if request.session['form_step'] == 1:
            agency_name = request.POST.get('nombre-agencia')
            address = request.POST.get('direccion')
            phone = request.POST.get('telefono')
            zip_code = request.POST.get('codigo-postal')

            if agency_name and address and phone and zip_code:
                request.session['agency_name'] = agency_name
                request.session['address'] = address
                request.session['phone'] = phone
                request.session['zip_code'] = zip_code

                request.session['form_step'] = 2
                return redirect('register_agency')
            else:
                return HttpResponse('Por favor completa todos los campos.')

        elif request.session['form_step'] == 2:
            if 'certificado' in request.FILES:
                certificate = request.FILES['certificado']
                fs = FileSystemStorage(location='static/certificates/')
                filename = fs.save(certificate.name, certificate)
                uploaded_file_url = fs.url(filename)

                agency, created = Agency.objects.update_or_create(
                    user=request.user,
                    defaults={
                        'agency_name': request.session['agency_name'],
                        'address': request.session['address'],
                        'phone': request.session['phone'],
                        'zip_code': request.session['zip_code'],
                        'certificate': uploaded_file_url,
                    }
                )

                if created:
                    for key in ['agency_name', 'address', 'phone', 'zip_code', 'form_step']:
                        del request.session[key]

                    return redirect('index')
                else:
                    return HttpResponse('La agencia ya esta registrada u ocurrio un error al ser guardado.')

            else:
                return HttpResponse('Por favor, sube un certificado valido.')

    step = request.session['form_step']
    return render(request, 'register_agency.html', {'step': step})


def seleccion_registro(request):
    """ Renderiza la pagina de seleccion. En caso de ya ser parte de un tipo de usuario, manda al main """
    if Client.objects.filter(user=request.user).exists() or Agency.objects.filter(user=request.user).exists():
        return redirect('index')

    return render(request, 'seleccion_registro.html')


def agencia_registro(request):
    return render(request, 'agencia_registro.html')


def viajero_registro(request):
    return render(request, 'viajero_registro.html')


def viajero_registro2(request):
    return render(request, 'viajero_registro2.html')


def validar_viajero(request):
    if request.method == 'POST':
        INE = request.FILES.get('INE')
        if INE:
            return HttpResponse('Certificado recibido.')
        else:
            return HttpResponse('No se recibió el certificado.', status=400)
    return render(request, 'validar_viajero.html')


def validar_agencia(request):
    if request.method == 'POST':
        certificado = request.FILES.get('certificado')
        return HttpResponse('Certificado recibido.')
    return render(request, 'validar_agencia.html')


def sobre_nosotros(request):
    return render(request, 'sobre_nosotros.html')


def terminos_y_condiciones(request):
    return render(request, 'terminos_y_condiciones.html')


def terminos_y_condiciones2(request):
    return render(request, 'terminos_y_condiciones2.html')


def terminos_legales(request):
    return render(request, 'terminos_legales.html')


def necesitas_ayuda(request):
    return render(request, 'necesitas_ayuda.html')

