from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('tours/', views.tours, name='tours'),
    path('tours/<int:pk>/', views.TourDetailView.as_view(), name='detalle_tour'),
    path('agencias/', views.agencias, name='agencias'),
    path('agencia/<int:pk>/', views.AgencyDetailView.as_view(),
         name='detalle_agencia'),
    path('filtro/', views.filtro_tour, name='filtro_tour'),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
