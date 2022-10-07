from django.contrib import admin
from django.template.response import TemplateResponse

from adminfilters.autocomplete import AutoCompleteFilter
from adminfilters.depot.widget import DepotManager
from adminfilters.filters import ChoicesFieldComboFilter, ValueFilter
from adminfilters.querystring import QueryStringFilter
from smart_admin.mixins import LinkedObjectsMixin

from ..utils.admin import (
    HOPEModelAdminBase,
    LastSyncDateResetMixin,
    SoftDeletableAdminMixin,
)
from .models import Program


@admin.register(Program)
class ProgramAdmin(SoftDeletableAdminMixin, LastSyncDateResetMixin, HOPEModelAdminBase):
    list_display = ("name", "status", "start_date", "end_date", "business_area")
    date_hierarchy = "start_date"
    list_filter = (
        ("status", ChoicesFieldComboFilter),
        ("business_area", AutoCompleteFilter),
        ("scope", ChoicesFieldComboFilter),
    )
    raw_id_fields = ("business_area",)
    filter_horizontal = ("admin_areas",)
