# Register your models here.
from django.contrib import admin


class NoDeleteMixin:
    def has_delete_permission(self, request, obj=None):
        return super().has_delete_permission(request, obj)


class HOPEModelAdminBase(NoDeleteMixin, admin.ModelAdmin):
    pass
