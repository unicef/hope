from django.contrib import admin
from smart_admin.mixins import DisplayAllMixin as SmartDisplayAllMixin


class HOPEModelAdminBase(SmartDisplayAllMixin, admin.ModelAdmin):
    list_per_page = 50

    def get_fields(self, request, obj=None):
        return super().get_fields(request, obj)

    def get_common_context(self, request, pk=None, **kwargs):
        opts = self.model._meta
        app_label = opts.app_label
        self.object = None

        context = {
            **self.admin_site.each_context(request),
            **kwargs,
            "opts": opts,
            "app_label": app_label,
        }
        if pk:
            self.object = self.get_object(request, pk)
            context["original"] = self.object
        return context
