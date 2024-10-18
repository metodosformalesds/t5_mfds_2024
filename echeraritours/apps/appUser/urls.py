from django.urls import path 
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('seleccion_registro', views.seleccion_registro, name='seleccion_registro'),
    path('agencia_registro/', views.agencia_registro, name='agencia_registro'),
    path('validar_agencia/', views.validar_agencia, name='validar_agencia'),
    path('validar_viajero/', views.validar_viajero, name='validar_viajero'),
    path('login', views.login, name='login'),
    path('sobre_nosotros', views.sobre_nosotros, name='sobre_nosotros'),
    path('viajero_registro', views.viajero_registro, name='viajero_registro'),
    path('viajero_registro2', views.viajero_registro2, name='viajero_registro2'),
]