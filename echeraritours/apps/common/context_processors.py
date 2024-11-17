"""Este archivo procesa un campo en comun que es verificar
    en que estado se encuentra el registro del usuario. Mas 
    especificamente, en si termino de registrarse o no como un
    cliente o una agencia para renderizar la opcion en el navbar.
"""
from apps.appUser.models import Client, Agency


def registration_status(request):
    is_client_registered = False
    is_agency_registered = False
    profile_image_url = None

    # Si el usuario ha iniciado sesión, se verifica
    if request.user.is_authenticated:
        client = Client.objects.filter(user=request.user).first()
        agency = Agency.objects.filter(user=request.user).first()

        if client:
            is_client_registered = True
            profile_image_url = client.profile_image.url if client.profile_image else None
        elif agency:
            is_agency_registered = True
            profile_image_url = agency.profile_image.url if agency.profile_image else None

    return {
        'is_client_registered': is_client_registered,
        'is_agency_registered': is_agency_registered,
        'profile_image_url': profile_image_url,
    }
