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
    path('agencia/dashboard/tours/', views.tours_dashboard, name='tours_dashboard'),
    path('agencia/dashboard/tours/crear/',
         views.CreateTour.as_view(), name='create_tour'),
    path('agencia/dashboard/metodos_pago/',
         views.payment_methods_agency, name='payment_methods_agency'),
    path('agencia/dashboard/reportes/', views.reports, name='reports'),
    path('agencia/dashboard/reportes/<int:tour_id>/',
         views.generate_report, name='generate_report'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
