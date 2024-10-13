from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def payments(request):
    return render(request, 'payments.html')