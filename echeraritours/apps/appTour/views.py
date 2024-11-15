from django.shortcuts import render, get_object_or_404
import requests
from django.http import HttpResponse
from django.views.generic import DetailView

from .models import Tour, Agency, Reviews
from apps.appDashboard.models import FavoriteList
from echeraritours import settings
from django.db.models import Q
from django.contrib import messages
from django.shortcuts import redirect

# Create your views here.


def tours(request):
    """
    Handles the retrieval and filtering of tour objects based on query parameters.
    Args:
        request (HttpRequest): The HTTP request object containing GET parameters for filtering.
    Returns:
        HttpResponse: The rendered HTML page displaying the filtered list of tours.
    Query Parameters:
        - precio (str, optional): The maximum price per person to filter tours.
        - lugar (str, optional): The place to filter tours by destination or place of origin.
    """
    tours = Tour.objects.all()
    reviews = Reviews.objects.order_by('-review_date')[:5]

    precio_max = request.GET.get('precio')
    if precio_max:
        tours = tours.filter(price_per_person__lte=precio_max)

    lugar = request.GET.get('lugar')
    if lugar:
        tours = tours.filter(
            Q(destination_place__icontains=lugar) |
            Q(place_of_origin__icontains=lugar)
        )

    return render(request, 'tour_templates/tours.html', {'tours': tours, 'reviews': reviews})


class TourDetailView(DetailView):
    """
    A view that displays the details of a specific tour.
    Attributes:
        model (Model): The model that this view will operate on, which is the Tour model.
        template_name (str): The path to the template that will be used to render the tour details.
        context_object_name (str): The name of the context variable that will contain the tour object.
    Methods:
        get_context_data(**kwargs):
            Adds the Google Maps API key to the context data.
    """
    model = Tour
    template_name = 'tour_templates/detalle_tour.html'
    context_object_name = 'tour'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['google_api'] = settings.GOOGLE_MAPS_API_KEY

        context['available_bookings'] = self.object.capacity - \
            self.object.total_bookings
        context['total_capacity'] = self.object.capacity

        if self.request.user.is_authenticated:
            context['show_booking_button'] = not Agency.objects.filter(
                user=self.request.user).exists()
        else:
            context['show_booking_button'] = True

        # Lo puse para poder jalar info del hotel que ponga la agencia
        place_url = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
        params = {
            'input': self.object.lodging_place,
            'inputtype': 'textquery',
            'fields': 'name,rating,formatted_address,photo',
            'key': context['google_api']
        }

        response = requests.get(place_url, params=params)
        candidates = response.json().get('candidates', [])

        # Verifica si hay resultados antes de acceder al primer elemento
        if candidates:
            place_data = candidates[0]

            # Extraer referencia de foto si existe
            if 'photos' in place_data:
                place_data['photo_reference'] = place_data['photos'][0].get(
                    'photo_reference')

            context['place_data'] = place_data
        else:
            context['place_data'] = {}

        return context


def add_favorite(request, pk):
    if request.user.is_authenticated:
        tour = get_object_or_404(Tour, pk=pk)
        client = request.user.client
        favorite_list, created = FavoriteList.objects.get_or_create(
            client=client)

        if not favorite_list.tours.filter(id=tour.id).exists():
            favorite_list.tours.add(tour)
            messages.success(
                request, 'El tour ha sido agregado a tus favoritos.')
        else:
            messages.info(request, 'Este tour ya está en tus favoritos.')

        return redirect('detalle_tour', pk=pk)
    else:
        messages.error(request, 'Debes iniciar sesión para agregar favoritos.')
        return redirect('login')


def agencias(request):
    """
    Handles the request to display a list of all agencies.

    This view function retrieves all Agency objects from the database and renders
    them in the 'tour_templates/agencias.html' template.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The rendered HTML page displaying the list of agencies.
    """
    agencias = Agency.objects.all()
    return render(request, 'tour_templates/agencias.html', {'agencias': agencias})


class AgencyDetailView(DetailView):
    """
    A view that displays the details of a specific travel agency.
    Attributes:
        model (Agency): The model that this view will operate on.
        template_name (str): The path to the template that will be used to render the view.
        context_object_name (str): The name of the context variable that will contain the agency object.
    Methods:
        get_context_data(**kwargs):
            Adds additional context data to the template, including tours and reviews related to the agency.
    """
    model = Agency
    template_name = 'tour_templates/detalle_agencia.html'
    context_object_name = 'agencia'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tours'] = Tour.objects.filter(agency=self.object)
        context['reviews'] = Reviews.objects.filter(
            reservation__tour__agency=self.object)
        return context


def filtro_tour(request):
    """
    Filters tours based on the place of origin, destination place, and start date provided in the request.
    Args:
        request (HttpRequest): The HTTP request object containing GET parameters for filtering.
    Returns:
        HttpResponse: The rendered HTML page with the filtered tours and the provided filter criteria.
    GET Parameters:
        - place_of_origin (str): The place of origin to filter tours by (optional).
        - destination_place (str): The destination place to filter tours by (optional).
        - start_date (str): The start date to filter tours by (optional).
    Context:
        - tours (QuerySet): The filtered queryset of Tour objects.
        - place_of_origin (str): The place of origin filter value.
        - destination_place (str): The destination place filter value.
        - start_date (str): The start date filter value.
    """
    place_of_origin = request.GET.get('place_of_origin', '')
    destination_place = request.GET.get('destination_place', '')
    start_date = request.GET.get('start_date', '')

    tours = Tour.objects.all()
    if place_of_origin:
        tours = tours.filter(place_of_origin__icontains=place_of_origin)
    if destination_place:
        tours = tours.filter(destination_place__icontains=destination_place)
    if start_date:
        tours = tours.filter(start_date__date=start_date)

    context = {
        'tours': tours,
        'place_of_origin': place_of_origin,
        'destination_place': destination_place,
        'start_date': start_date,
    }
    return render(request, 'tour_templates/filtro_tour.html', context)
