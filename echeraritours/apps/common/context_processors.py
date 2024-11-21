from apps.appUser.models import Client, Agency


def registration_status(request):
    """
    Author: Santiago Mendivil
    Determines the registration status of the user and retrieves the profile image URL if available.
    Args:
        request (HttpRequest): The HTTP request object containing user information.
    Returns:
        dict: A dictionary containing the following keys:
            - 'is_client_registered' (bool): True if the user is registered as a client, False otherwise.
            - 'is_agency_registered' (bool): True if the user is registered as an agency, False otherwise.
            - 'profile_image_url' (str or None): The URL of the user's profile image if available, otherwise None.
    """
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
