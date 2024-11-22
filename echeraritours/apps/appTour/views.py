from django.urls import reverse
from django.shortcuts import render, get_object_or_404
import requests
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.views.generic import DetailView

from .models import Tour, Agency, Reviews
from apps.appDashboard.models import FavoriteList
from echeraritours import settings
from django.db.models import Q
from django.contrib import messages
from django.shortcuts import redirect
from .models import models

# Create your views here.


def tours(request):
    """
    Author: Leonardo Ortega 
    Handles the retrieval and filtering of tour objects based on query parameters.
    Args:
        request (HttpRequest): The HTTP request object containing GET parameters for filtering.
    Returns:
        HttpResponse: The rendered HTML page displaying the filtered list of tours.
    Query Parameters:
        - precio (str, optional): The maximum price per person to filter tours.
        - destination_place (str, optional): The place to filter tours by destination.
    """
    tours_list = Tour.objects.all()
    reviews = Reviews.objects.filter(
        reservation__tour__in=tours_list).order_by('-review_date')[:3]

    max_price = request.GET.get('precio')
    if max_price:
        tours_list = tours_list.filter(price_per_person__lte=max_price)

    destination_place = request.GET.get('destination_place')
    if destination_place:
        tours_list = tours_list.filter(
            destination_place__icontains=destination_place)

    paginator = Paginator(tours_list, 6)  # Show 8 tours per page
    page_number = request.GET.get('page')
    tours = paginator.get_page(page_number)
    reviews = Reviews.objects.order_by('-review_date')[:5]

    return render(request, 'tour_templates/tours.html', {'tours': tours, 'reviews': reviews})


class TourDetailView(DetailView):
    """
    Authors: Hector Ramos, Santiago Mendivil
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

        context['reviews'] = Reviews.objects.filter(reservation__tour=self.object)
        context['rating'] = Reviews.objects.filter(reservation__tour=self.object).aggregate(models.Avg('rating'))['rating__avg']

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
    """
    Author: Santiago Mendivil
    Adds a tour to the user's list of favorite tours.
    If the user is authenticated, the function retrieves the tour specified by the primary key (pk)
    and the user's client profile. It then checks if the tour is already in the user's favorite list.
    If not, the tour is added to the list and a success message is displayed. If the tour is already
    in the favorite list, an informational message is displayed. The user is then redirected to the
    tour detail page.
    If the user is not authenticated, an error message is displayed and the user is redirected to the
    login page.
    Args:
        request (HttpRequest): The HTTP request object.
        pk (int): The primary key of the tour to be added to favorites.
    Returns:
        HttpResponse: A redirect to the tour detail page if the user is authenticated, or to the login
        page if the user is not authenticated.
    """

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
    Author: Leonardo Ortega
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
    Author: Santiago Mendivil
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
        context['google_api'] = settings.GOOGLE_MAPS_API_KEY
        context['reviews'] = Reviews.objects.filter(
            reservation__tour__agency=self.object)
        context['rating'] = Reviews.objects.filter(
            reservation__tour__agency=self.object).aggregate(models.Avg('rating'))['rating__avg']
        context['mail'] = Agency.objects.get(id=self.object.id).user.email
        return context


def filtro_tour(request):
    """
    Author: Leonardo Ortega
    Handles the retrieval and filtering of tour objects based on query parameters.
    Args:
        request (HttpRequest): The HTTP request object containing GET parameters for filtering.
    Returns:
        HttpResponse: The rendered HTML page displaying the filtered list of tours.
    Query Parameters:
        - precio (str, optional): The maximum price per person to filter tours.
        - lugar (str, optional): The place to filter tours by destination or place of origin.
    """
    from django.core.paginator import Paginator

    tours_list = Tour.objects.all()
    reviews = Reviews.objects.filter(
        reservation__tour__in=tours_list).order_by('-review_date')[:5]
    max_price = request.GET.get('precio')
    if max_price:
        tours_list = tours_list.filter(price_per_person__lte=max_price)

    lugar = request.GET.get('lugar')
    if lugar:
        tours_list = tours_list.filter(
            Q(destination_place__icontains=lugar)
        )

    paginator = Paginator(tours_list, 10)  # Show 10 tours per page
    page_number = request.GET.get('page')
    tours = paginator.get_page(page_number)
    reviews = Reviews.objects.order_by('-review_date')[:5]

    return render(request, 'tour_templates/tours.html', {'tours': tours, 'reviews': reviews})
