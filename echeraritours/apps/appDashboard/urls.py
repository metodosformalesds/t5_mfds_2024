from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
     path('', views.dashboard, name='dashboard'),
     path('cliente/dashboard/', views.client_dashboard, name='client_dashboard'),
     path('cliente/dashboard/planes_activos/',
          views.client_active_plans, name='client_active_plans'),
     path('cliente/dashboard/planes_activos/detalles/<int:reservation_pk>/',
          views.PlanDetailView.as_view(), name='plan_detail'),
     path('cliente/dashboard/planes_activos/detalles/<int:reservation_pk>/ticket/',
          views.ticket, name='ticket'),
     path('cliente/dashboard/perfil/', views.client_profile, name='client_profile'),
     path('cliente/dashboard/metodos_pago/',
          views.payment_methods_client, name='payment_methods_client'),
     path('cliente/dashboard/agregar_metodo_pago/',
          views.add_payment_method, name='add_payment_method'),
     path('cliente/dashboard/favoritos/', views.favorites, name='favorites'),
     path('cliente/dashboard/favoritos/eliminar/<int:tour_id>/',
          views.delete_favorite, name='delete_favorite'),
     path('cliente/dashboard/historial',
          views.client_purchases, name='client_purchases'),
     path('cliente/dashboard/reseñas/<int:reservation_id>/',
          views.CreateReview.as_view(), name="create_review"),
     path('cliente/dashboard/reseñas/eliminar/<int:pk>/',
          views.DeleteReview.as_view(), name='delete_review'),
     path('cliente/dashboard/metodos_pago/<int:metodo_id>/predeterminado/', 
          views.set_default_payment_method, name='set_default_payment_method'),
     path('cliente/dashboard/eliminar_metodo_pago/<int:metodo_id>/', 
          views.delete_payment_method, name='delete_payment_method'),



     path('agencia/dashboard/', views.agency_dashboard, name='agency_dashboard'),
     path('agencia/dashboard/tours/', views.tours_dashboard, name='tours_dashboard'),
     path('agencia/dashboard/tours/crear/',
          views.CreateTour.as_view(), name='create_tour'),
     path('agencia/dashboard/perfil/', views.agency_profile, name='agency_profile'),
     path('agencia/dashboard/metodos_pago/',
          views.payment_methods_agency, name='payment_methods_agency'),
     path('agencia/dashboard/agregar_metodos_pago/', 
          views.add_payment_methods_agency, name='add_payment_methods_agency'),
     path('agencia/dashboard/eliminar_metodo_pago/<int:metodo_id>/', 
          views.delete_payment_method, name='delete_payment_method'),
     path('agencia/dashboard/reportes/', views.reports, name='reports'),
     path('agencia/dashboard/reportes/<int:tour_id>/',
          views.generate_report, name='generate_report'),

]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
