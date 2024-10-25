from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from apps.appUser.models import Client, Agency


# Create your views here.


@login_required(login_url='login')
def dashboard(request):
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
    return render(request, 'client_dashboard.html')


@login_required(login_url='login')
def agency_dashboard(request):
    return render(request, 'agency_dashboard.html')
