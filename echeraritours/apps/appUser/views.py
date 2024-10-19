from django.shortcuts import render, redirect
from django.http import HttpResponse

# Para los formularios
from django.contrib.auth.forms import UserCreationForm
from .forms import CreateUserForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout

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

    Esta funcion maneja procesamiento de la informacion enviada por el usuario. 
    Si la solicitud es de tipo POST y el formulario es valido, entonces se guarda el nuevo 
    usuario en la base de datos, mas especifico en la tabla User.

    Args:
        request (HttpRequest): Objeto que contiene informacion sobre la solicitud 
                               HTTP realizada por el usuario.

    Returns:
        HttpResponse: Renderiza la plantilla 'register.html' con el formulario, ya sea 
                      vacio (en una solicitud GET) o con datos (en una solicitud POST).
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
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            messages.info(request, 'El correo o contraseña son incorrectos')

    context = {}
    return render(request, 'login.html', context)


def logoutUser(request):
    logout(request)
    return redirect('login')


def seleccion_registro(request):
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
    pass


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
