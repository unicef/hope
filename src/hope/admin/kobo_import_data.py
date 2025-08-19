import logging

from adminfilters.autocomplete import AutoCompleteFilter
from django.contrib import admin

from hope.admin.utils import HOPEModelAdminBase
from hope.apps.registration_data.models import KoboImportData

logger = logging.getLogger(__name__)


@admin.register(KoboImportData)
class KoboImportDataDataAdmin(HOPEModelAdminBase):
    search_fields = ("business_area_slug",)
    list_display = (
        "business_area_slug",
        "status",
        "data_type",
        "kobo_asset_id",
        "number_of_households",
        "number_of_individuals",
        "only_active_submissions",
        "pull_pictures",
    )
    list_filter = (
        "status",
        "data_type",
        ("created_by_id", AutoCompleteFilter),
        "only_active_submissions",
        "pull_pictures",
    )
