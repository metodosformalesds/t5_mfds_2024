from django.urls import path 
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('agencia_registro/', views.agencia_registro),
    path('validar_agencia/', views.validar_agencia),
]