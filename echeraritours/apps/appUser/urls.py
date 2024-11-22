from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .views import (solicitar_correo,
                    verificar_codigo,
                    restablecer_contrasena,
                    )
from django.conf import settings
from django.conf.urls.static import static

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

    # recuperacion de contraseña
    path('solicitar_correo/', views.solicitar_correo, name='solicitar_correo'),
    path('verificar_codigo/', views.verificar_codigo, name='verificar_codigo'),
    path('restablecer_contrasena/', views.restablecer_contrasena,
         name='restablecer_contrasena'),

    # Reglas de negocio
    path('sobre_nosotros/', views.sobre_nosotros, name='sobre_nosotros'),
    path('terminos_y_condiciones/', views.terminos_y_condiciones,
         name='terminos_y_condiciones'),
    path('terminos_y_condiciones2/', views.terminos_y_condiciones2,
         name='terminos_y_condiciones2'),
    path('terminos_legales/', views.terminos_legales, name='terminos_legales'),
    path('necesitas_ayuda', views.necesitas_ayuda, name='necesitas_ayuda'),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
