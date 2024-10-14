from django.contrib import admin
from .models import Tour, Reservation, Reviews

# Register your models here.
admin.site.register(Tour)
admin.site.register(Reservation)
admin.site.register(Reviews)
