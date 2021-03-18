from adminfilters.filters import TextFieldFilter
from django.contrib import admin

from hct_mis_api.apps.utils.admin import HOPEModelAdminBase
from hct_mis_api.apps.mis_datahub.models import (
    Household,
    Individual,
    Session,
    TargetPopulation,
    Program,
    IndividualRoleInHousehold,
    Document,
)


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
class SessionAdmin(admin.ModelAdmin):
    list_display = ("timestamp", "id", "source", "status", "last_modified_date", "business_area")
    date_hierarchy = "timestamp"
    list_filter = ("status", "source", TextFieldFilter.factory("business_area"))
    ordering = ("timestamp",)


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
