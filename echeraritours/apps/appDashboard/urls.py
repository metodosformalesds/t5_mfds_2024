from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('cliente/dashboard/', views.client_dashboard, name='client_dashboard'),
    path('agencia/dashboard/', views.agency_dashboard, name='agency_dashboard'),
]
