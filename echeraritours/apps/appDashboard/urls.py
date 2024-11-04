from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('cliente/dashboard/', views.client_dashboard, name='client_dashboard'),
    path('cliente/dashboard/planes_activos/',
         views.client_active_plans, name='client_active_plans'),
    path('cliente/dashboard/perfil/', views.client_profile, name='client_profile'),
    path('agencia/dashboard/', views.agency_dashboard, name='agency_dashboard'),
]
