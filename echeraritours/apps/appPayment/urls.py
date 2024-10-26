from django.urls import path
from . import views

urlpatterns = [
    path('detalles_reservacion/', views.detalles_reservacion, name='detalles_reservacion'),
    path('pago_reservacion/', views.pago_reservacion, name='pago_reservacion'),
    path('final_reservacion/', views.final_reservacion, name='final_reservacion'),
]
