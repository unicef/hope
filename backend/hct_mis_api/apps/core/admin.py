from django.contrib import admin

from core.models import Location, BusinessArea


@admin.register(BusinessArea)
class BusinessAreaAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
