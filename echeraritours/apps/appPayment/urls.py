from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from .views import pago_exitoso_view, pago_cancelado_view, detalles_reservacion
from apps.appPayment.views import detalles_reservacion


urlpatterns = [
     path('detalles_reservacion/<int:id>/', views.detalles_reservacion, name='detalles_reservacion'),
     path('pago_completado/', views.pago_completado, name='pago_completado'),
     path('seleccion_pago/<int:id>/', views.seleccion_pago, name='seleccion_pago'),
     path('realizar_pago_paypal/<int:id>/', views.realizar_pago_paypal, name='realizar_pago_paypal'),
]


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
