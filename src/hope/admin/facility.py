from adminfilters.autocomplete import AutoCompleteFilter
from django.contrib import admin

from hope.admin.utils import HOPEModelAdminBase
from hope.models import Facility


@admin.register(Facility)
class FacilityAdmin(HOPEModelAdminBase):
    list_display = (
        "name",
        "admin_area",
        "business_area",
    )
    list_filter = ("name", ("business_area", AutoCompleteFilter), ("admin_area", AutoCompleteFilter))
    search_fields = ("name",)
    ordering = ("name",)
