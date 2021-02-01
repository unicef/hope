# Register your models here.
from django.contrib import admin
from django.db import models
from django.contrib.admin.utils import flatten


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


class SmartFieldsetMixin:

    def get_fieldsets(self, request, obj=None):
        all_fields = self.get_fields(request, obj)
        selected = []

        if self.fieldsets:
            fieldsets = list(self.fieldsets)
        else:
            fieldsets = [(None, {'fields': all_fields})]

        for e in fieldsets:
            selected.extend(flatten(e[1]['fields']))
        for e in fieldsets:
            if e[1]['fields'] == ('__all__',):
                __all = [e for e in all_fields if e not in selected]
                e[1]['fields'] = __all
                break
        return fieldsets


class HOPEModelAdminBase(NeedRootMixin, DisplayAllMixin, admin.ModelAdmin):
    list_per_page = 50

    def get_fields(self, request, obj=None):
        return super().get_fields(request, obj)
