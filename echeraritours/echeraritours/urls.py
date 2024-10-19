from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.appUser.urls')),  
    path('tour/', include('apps.appTour.urls')),  #
    path('payments/', include('apps.appPayment.urls')),
    path('dashboard/', include('apps.appDashboard.urls')),
    # path('social/', include('social_django.urls', namespace='social')), esta al rato sale
]
