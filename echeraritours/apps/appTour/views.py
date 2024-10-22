from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def tours(request):
    return render(request, 'tours.html')

def agencias(request):
    return render(request, 'agencias.html')

