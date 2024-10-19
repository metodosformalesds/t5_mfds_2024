from django.urls import path
from . import views

urlpatterns = [
    # Vistas generales
    path('', views.index, name='index'),
    path('register/', views.registerPage, name='register'),
    path('login/', views.loginPage, name='login'),
    path('logout/', views.logoutUser, name='logout'),
    path('seleccion_registro/', views.seleccion_registro,
         name='seleccion_registro'),

    # Registro de agencia,
    path('agencia_registro/', views.agencia_registro, name='agencia_registro'),
    path('validar_agencia/', views.validar_agencia, name='validar_agencia'),

    # Registro de viajero
    path('viajero_registro/', views.viajero_registro, name='viajero_registro'),
    path('viajero_registro2/', views.viajero_registro2, name='viajero_registro2'),
    path('validar_viajero/', views.validar_viajero, name='validar_viajero'),

    # Reglas de negocio
    path('sobre_nosotros/', views.sobre_nosotros, name='sobre_nosotros'),
    path('terminos_y_condiciones/', views.terminos_y_condiciones,
         name='terminos_y_condiciones'),
    path('terminos_y_condiciones2/', views.terminos_y_condiciones2,
         name='terminos_y_condiciones2'),
    path('terminos_legales/', views.terminos_legales, name='terminos_legales'),
]
