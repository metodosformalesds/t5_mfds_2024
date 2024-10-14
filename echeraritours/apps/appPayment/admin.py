from django.contrib import admin
from .models import PaymentMethod, Payments

# Register your models here.
admin.site.register(Payments)
admin.site.register(PaymentMethod)
