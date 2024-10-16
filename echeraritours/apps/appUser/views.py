from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def index(request):
    return render(request, 'index.html')

def agencia_registro(request):
    return render(request, 'agencia_registro.html')

def validar_agencia(request):
    if request.method == 'POST':
        certificado = request.FILES.get('certificado')
        return HttpResponse('Certificado recibido.')
    return render(request, 'validar_agencia.html')