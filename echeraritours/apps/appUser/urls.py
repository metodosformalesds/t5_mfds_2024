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

     # Registro especifico
     path('registrar_cliente/', views.registerClient, name='register_client'),
     path('registrar_agencia/', views.registerAgency, name='register_agency'),

     # Reglas de negocio
     path('sobre_nosotros/', views.sobre_nosotros, name='sobre_nosotros'),
     path('terminos_y_condiciones/', views.terminos_y_condiciones,
          name='terminos_y_condiciones'),
     path('terminos_y_condiciones2/', views.terminos_y_condiciones2,
          name='terminos_y_condiciones2'),
     path('terminos_legales/', views.terminos_legales, name='terminos_legales'),
     path('necesitas_ayuda', views.necesitas_ayuda, name='necesitas_ayuda'),
]
