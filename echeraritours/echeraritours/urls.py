from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.appUser.urls')),  
    path('tour/', include('apps.appTour.urls')),  # Incluye las rutas de appTours bajo 'tour/'
    path('payments/', include('apps.appPayment.urls')),
    path('dashboard/', include('apps.appDashboard.urls')),
]
