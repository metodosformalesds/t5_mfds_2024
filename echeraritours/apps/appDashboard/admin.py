from django.contrib import admin
from .models import Reports, FavoriteList

# Register your models here.


class FavoriteListAdmin(admin.ModelAdmin):
    list_display = ('client',)
    filter_horizontal = ('tours',)


admin.site.register(Reports)
admin.site.register(FavoriteList, FavoriteListAdmin)
