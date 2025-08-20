import logging

from adminfilters.autocomplete import AutoCompleteFilter
from adminfilters.mixin import AdminFiltersMixin
from django.contrib import admin

from hope.apps.core.forms import DataCollectingTypeForm
from hope.apps.core.models import DataCollectingType

logger = logging.getLogger(__name__)


@admin.register(DataCollectingType)
class DataCollectingTypeAdmin(AdminFiltersMixin, admin.ModelAdmin):
    form = DataCollectingTypeForm

    list_display = (
        "label",
        "code",
        "type",
        "active",
        "deprecated",
        "individual_filters_available",
        "household_filters_available",
        "recalculate_composition",
        "weight",
    )
    list_filter = (
        ("limit_to", AutoCompleteFilter),
        "type",
        "active",
        "individual_filters_available",
        "household_filters_available",
        "recalculate_composition",
    )
    filter_horizontal = ("compatible_types", "limit_to")
    search_fields = (
        "label",
        "code",
    )
