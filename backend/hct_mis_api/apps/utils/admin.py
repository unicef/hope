# Register your models here.
from django.contrib import admin
from django.db import models


class NeedRootMixin:
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_add_permission(self, request):
        return request.user.is_superuser


class ReadOnlyMixin:
    actions = None

    def get_readonly_fields(self, request, obj=None):
        return [field.name for field in self.model._meta.fields]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class DisplayAllMixin:
    def get_list_display(self, request):  # pragma: no cover
        if self.list_display == ('__str__',):
            return [field.name for field in self.model._meta.fields
                    if not isinstance(field, models.ForeignKey)]

        return self.list_display



class HOPEModelAdminBase(NeedRootMixin, DisplayAllMixin, admin.ModelAdmin):
    list_per_page = 50
