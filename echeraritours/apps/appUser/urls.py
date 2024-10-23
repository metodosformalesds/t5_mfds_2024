from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .views import (recuperar_contra,
                    envio_contra,  
                    completo_contra,
                    confirmar_contra,
                    )

urlpatterns = [
     # Vistas generales
     path('', views.index, name='index'),
     path('register/', views.registerPage, name='register'),
     path('login/', views.loginPage, name='login'),
     path('logout/', views.logoutUser, name='logout'),
     path('seleccion_registro/', views.seleccion_registro,
          name='seleccion_registro'),

    # Registro especifico
    path('registrar_cliente/', views.registrar_cliente, name='registrar_cliente'),
    path('registrar_agencia/', views.registrar_agencia, name='registrar_agencia'),

   # Recuperación de contraseña
    path('recuperar_contra/', views.recuperar_contra, name='recuperar_contra'),
    path('envio_contra/', views.envio_contra, name='envio_contra'), 
    path('confirmar_contra/<uidb64>/<token>/', views.confirmar_contra, name='confirmar_contra'),
    path('completo_contra/', views.completo_contra, name='recuperar_contra_completo'),

     # Reglas de negocio
     path('sobre_nosotros/', views.sobre_nosotros, name='sobre_nosotros'),
     path('terminos_y_condiciones/', views.terminos_y_condiciones,
          name='terminos_y_condiciones'),
     path('terminos_y_condiciones2/', views.terminos_y_condiciones2,
          name='terminos_y_condiciones2'),
     path('terminos_legales/', views.terminos_legales, name='terminos_legales'),
     path('necesitas_ayuda', views.necesitas_ayuda, name='necesitas_ayuda'),

]
