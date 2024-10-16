from django.urls import path 
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('seleccion_registro', views.seleccion_registro, name='seleccion_registro'),
    path('agencia_registro/', views.agencia_registro, name='agencia_registro'),
    path('validar_agencia/', views.validar_agencia, name='validar_agencia'),
    path('login', views.login, name='login'),
    path('sobre_nosotros', views.sobre_nosotros, name='sobre_nosotros'),
]