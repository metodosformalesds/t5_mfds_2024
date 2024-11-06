from django.urls import path
from . import views
from .views import pago_exitoso_view, pago_cancelado_view, detalles_reservacion
from apps.appPayment.views import detalles_reservacion


urlpatterns = [
    path('detalles_reservacion/<int:tour_id>/', views.detalles_reservacion, name='detalles_reservacion'),
    path('pago_reservacion/<int:tour_id>/', views.pago_reservacion, name='pago_reservacion'),
    path('pago/exitoso/', views.pago_exitoso_view, name="pago_exitoso"),
    path('pago/cancelado/', views.pago_cancelado_view, name="pago_cancelado"),
    path('final_reservacion/', views.final_reservacion, name='final_reservacion'),
]

