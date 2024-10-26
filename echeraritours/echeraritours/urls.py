from django.contrib import admin
from django.urls import path, include
from apps.appPayment import views  

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.appUser.urls')),  
    path('tour/', include('apps.appTour.urls')), 
    path('dashboard/', include('apps.appDashboard.urls')),
    path('payment/', include('apps.appPayment.urls')),
    
    # path('social/', include('social_django.urls', namespace='social')), esta al rato sale
]
