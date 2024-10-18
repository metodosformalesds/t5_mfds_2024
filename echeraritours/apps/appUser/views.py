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


def login(request):
    return render(request, 'login.html')

def sobre_nosotros(request):
    return render(request, 'sobre_nosotros.html')

def terminos_y_condiciones(request):
    return render(request, 'terminos_y_condiciones.html')

def terminos_y_condiciones2(request):
    return render(request, 'terminos_y_condiciones2.html')
