from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from .views import pago_exitoso_view, pago_cancelado_view, detalles_reservacion
from apps.appPayment.views import detalles_reservacion


urlpatterns = [
    path('detalles_reservacion/<int:tour_id>/',
         views.detalles_reservacion, name='detalles_reservacion'),  # Detalles reservacion SI
    path('pago_reservacion/<int:tour_id>/',
         views.pago_reservacion, name='pago_reservacion'),
    path('pago_completado/<int:tour_id>/',
         views.pago_completado, name='pago_completado'),
    path('pago/exitoso/', views.pago_exitoso_view, name="pago_exitoso"),
    path('pago/cancelado/', views.pago_cancelado_view, name="pago_cancelado"),
    path('realizar_pago_stripe/', views.realizar_pago_stripe,
         name='realizar_pago_stripe'),
    path('stripe/webhook/', views.stripe_webhook, name='stripe_webhook'),
    path('process_payment', views.process_payment, name='process_payment'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
