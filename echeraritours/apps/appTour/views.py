from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def tour_list(request):
    return render(request, 'tour_templates/tour_list.html')

def tour_detail(request):
    return render(request, 'tour_templates/tour_detail.html')

