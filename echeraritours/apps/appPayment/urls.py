from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('detalles_reservacion/<int:id>/',
         views.detalles_reservacion, name='detalles_reservacion'),
    path('pago_completado/', views.pago_completado, name='pago_completado'),
    path('realizar_pago_stripe/', views.realizar_pago_stripe,
         name='realizar_pago_stripe'),
    path('stripe/webhook/', views.stripe_webhook, name='stripe_webhook'),
    path('process_payment', views.process_payment, name='process_payment'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
