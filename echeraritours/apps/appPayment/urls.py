from django.urls import path
from . import views

urlpatterns = [
    path('detalles_reservacion/<int:tour_id>/', views.detalles_reservacion, name='detalles_reservacion'),
    path('pago_reservacion/<int:tour_id>/', views.pago_reservacion, name='pago_reservacion'),
    path('final_reservacion/', views.final_reservacion, name='final_reservacion'),
]
