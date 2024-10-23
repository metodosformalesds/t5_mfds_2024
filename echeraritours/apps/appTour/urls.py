from django.urls import path
from . import views

urlpatterns = [
    path('tours/', views.tours, name='tours'),
    path('agencias/', views.agencias, name='agencias'),
    path('filtro/', views.filtro_tour, name='filtro_tour'),
]