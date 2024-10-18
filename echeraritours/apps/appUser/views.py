from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def index(request):
    return render(request, 'index.html')

def seleccion_registro(request):
    return render(request, 'seleccion_registro.html')

def agencia_registro(request):
    return render(request, 'agencia_registro.html')

def viajero_registro(request):
    return render(request, 'viajero_registro.html')

def viajero_registro2(request):
    return render(request, 'viajero_registro2.html')

def validar_viajero(request):
    return render(request, 'validar_viajero.html')

def validar_agencia(request):
    if request.method == 'POST':
        certificado = request.FILES.get('certificado')
        return HttpResponse('Certificado recibido.')
    return render(request, 'validar_agencia.html')


def login(request):
    return render(request, 'login.html')

def sobre_nosotros(request):
    return render(request, 'sobre_nosotros.html')