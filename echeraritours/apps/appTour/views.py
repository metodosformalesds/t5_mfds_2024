from django.shortcuts import render
from django.http import HttpResponse

from .models import Tour

# Create your views here.
def tours(request):
    return render(request, 'tour_templates/tours.html')

def agencias(request):
    return render(request, 'agencias.html')

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
