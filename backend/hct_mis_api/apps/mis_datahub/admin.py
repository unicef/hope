from django.contrib import admin
from django.template.response import TemplateResponse

from admin_extra_urls.decorators import button
from admin_extra_urls.mixins import ExtraUrlMixin
from adminfilters.filters import TextFieldFilter
from smart_admin.mixins import FieldsetMixin as SmartFieldsetMixin

from hct_mis_api.apps.mis_datahub.models import (
    Document,
    Household,
    Individual,
    IndividualRoleInHousehold,
    Program,
    Session,
    TargetPopulation,
)
from hct_mis_api.apps.utils.admin import HOPEModelAdminBase


@admin.register(Household)
class HouseholdAdmin(HOPEModelAdminBase):
    list_filter = (TextFieldFilter.factory("session__id"), TextFieldFilter.factory("business_area"))
    raw_id_fields = ("session",)


@admin.register(Individual)
class IndividualAdmin(HOPEModelAdminBase):
    list_display = ("unicef_id", "family_name", "given_name")
    list_filter = (TextFieldFilter.factory("session__id"), TextFieldFilter.factory("business_area"))
    raw_id_fields = ("session",)


@admin.register(IndividualRoleInHousehold)
class IndividualRoleInHouseholdAdmin(HOPEModelAdminBase):
    list_filter = (TextFieldFilter.factory("session__id"), TextFieldFilter.factory("business_area"))


@admin.register(Session)
class SessionAdmin(SmartFieldsetMixin, ExtraUrlMixin, admin.ModelAdmin):
    list_display = ("timestamp", "id", "source", "status", "last_modified_date", "business_area")
    date_hierarchy = "timestamp"
    list_filter = ("status", "source", TextFieldFilter.factory("business_area"))
    ordering = ("timestamp",)

    @button()
    def inspect(self, request, pk):
        context = self.get_common_context(request)
        return TemplateResponse(request, "admin/mis_datahub/session/inspect.html", context)


@admin.register(TargetPopulation)
class TargetPopulationAdmin(HOPEModelAdminBase):
    list_filter = (TextFieldFilter.factory("session__id"), TextFieldFilter.factory("business_area"))
    raw_id_fields = ("session",)


@admin.register(Program)
class ProgramAdmin(HOPEModelAdminBase):
    list_filter = (TextFieldFilter.factory("session__id"), TextFieldFilter.factory("business_area"))


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ("type", "number")
    list_filter = (TextFieldFilter.factory("session__id"), TextFieldFilter.factory("business_area"))
    raw_id_fields = ("session",)
