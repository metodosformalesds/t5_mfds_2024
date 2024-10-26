"""Este archivo procesa un campo en comun que es verificar
    en que estado se encuentra el registro del usuario. Mas 
    especificamente, en si termino de registrarse o no como un
    cliente o una agencia para renderizar la opcion en el navbar.
"""
from apps.appUser.models import Client, Agency


def registration_status(request):
    is_client_registered = False
    is_agency_registered = False

    # Si el usuario si inicio sesion, se verifica
    if request.user.is_authenticated:
        is_client_registered = Client.objects.filter(
            user=request.user).exists()
        is_agency_registered = Agency.objects.filter(
            user=request.user).exists()

    return {
        'is_client_registered': is_client_registered,
        'is_agency_registered': is_agency_registered,
    }
