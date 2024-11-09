from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('cliente/dashboard/', views.client_dashboard, name='client_dashboard'),
    path('cliente/dashboard/planes_activos/',
         views.client_active_plans, name='client_active_plans'),
    path('cliente/dashboard/perfil/', views.client_profile, name='client_profile'),
    path('cliente/dashboard/metodos_pago/',
         views.payment_methods_client, name='payment_methods_client'),
    path('cliente/dashboard/agregar_metodo_pago/',
         views.add_payment_method, name='add_payment_method'),
    path('agencia/dashboard/', views.agency_dashboard, name='agency_dashboard'),
    path('agencia/dashboard/reportes/', views.reports, name='reports'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
