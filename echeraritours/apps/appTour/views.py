from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import DetailView

from .models import Tour, Agency
from django.db.models import Q

# Create your views here.


def tours(request):
    tours = Tour.objects.all()

    # Filtrar por precio máximo
    precio_max = request.GET.get('precio')
    if precio_max:
        tours = tours.filter(price_per_person__lte=precio_max)

    # Filtrar por lugar (en destino o lugar de origen)
    lugar = request.GET.get('lugar')
    if lugar:
        tours = tours.filter(
            Q(destination_place__icontains=lugar) |
            Q(place_of_origin__icontains=lugar)
        )

    return render(request, 'tour_templates/tours.html', {'tours': tours})


class TourDetailView(DetailView):
    model = Tour
    template_name = 'tour_templates/detalle_tour.html'
    context_object_name = 'tour'


def agencias(request):
    agencias = Agency.objects.all()
    return render(request, 'tour_templates/agencias.html', {'agencias': agencias})

class AgencyDetailView(DetailView):
    model = Agency

    template_name = 'tour_templates/detalle_agencia.html' 
    context_object_name = 'agencia'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Aqui hace que solo los tours relacionados con la agencia se vayan a mostrar
        context['tours'] = Tour.objects.filter(agency=self.object)
        return context


def filtro_tour(request):
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
