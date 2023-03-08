import logging

from django.contrib import admin

from admin_extra_buttons.decorators import button, view
from admin_extra_buttons.mixins import ExtraButtonsMixin
from smart_admin.decorators import smart_register

from hct_mis_api.apps.program.models import Program
from hct_mis_api.aurora import models

logger = logging.getLogger(__name__)


@smart_register(models.Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "business_area")
    readonly_fields = (
        "name",
        "slug",
    )


@smart_register(models.Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("name", "organization")
    list_filter = ("organization", "programme")
    readonly_fields = ("name", "organization")

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields["programme"].queryset = Program.objects.filter(business_area=obj.business_area)
        return form


@smart_register(models.Registration)
class RegistrationAdmin(ExtraButtonsMixin, admin.ModelAdmin):
    list_display = ("name", "project", "rdi_policy", "project")
    readonly_fields = ("name", "project", "slug", "extra", "metadata")
    list_filter = ("rdi_policy", "project")

    @button()
    def analyze(self, request, pk):
        pass

    @view()
    def _analyze(self, request, pk):
        pass


@smart_register(models.Record)
class RecordAdmin(admin.ModelAdmin):
    pass
