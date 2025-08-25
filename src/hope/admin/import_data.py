import logging

from adminfilters.autocomplete import AutoCompleteFilter
from django.contrib import admin

from hope.admin.utils import HOPEModelAdminBase
from hope.models.registration_data import ImportData

logger = logging.getLogger(__name__)


@admin.register(ImportData)
class ImportDataAdmin(HOPEModelAdminBase):
    search_fields = ("business_area_slug",)
    list_display = (
        "business_area_slug",
        "status",
        "data_type",
        "number_of_households",
        "number_of_individuals",
    )
    list_filter = (
        "status",
        "data_type",
        ("created_by_id", AutoCompleteFilter),
    )
