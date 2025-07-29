import logging
from typing import TYPE_CHECKING

from django.contrib import admin

from adminfilters.autocomplete import AutoCompleteFilter
from adminfilters.mixin import AdminFiltersMixin

from hct_mis_api.apps.core.forms import DataCollectingTypeForm
from hct_mis_api.apps.core.models import (
    DataCollectingType,
)

if TYPE_CHECKING:
    from django.contrib.admin import ModelAdmin


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
