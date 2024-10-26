from django.urls import path
from . import views

urlpatterns = [
    path('tours/', views.tours, name='tours'),
    path('tours/<int:pk>/', views.TourDetailView.as_view(), name='detalle_tour'),
    path('agencias/', views.agencias, name='agencias'),
    path('agencia/<int:pk>/', views.AgencyDetailView.as_view(), name='detalle_agencia'),
    path('filtro/', views.filtro_tour, name='filtro_tour'),
]
