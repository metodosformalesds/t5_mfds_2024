from django.urls import path
from . import views

urlpatterns = [
    path('detalles_reservacion/<int:id>/',
        views.detalles_reservacion, name='detalles_reservacion'),
    path('realizar_pago_stripe/', views.realizar_pago_stripe, name='realizar_pago_stripe'),
    path('stripe/webhook/', views.stripe_webhook, name='stripe_webhook'),
    path('process_payment', views.process_payment, name='process_payment'),
]
