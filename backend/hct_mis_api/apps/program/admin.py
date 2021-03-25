from django.contrib import admin

from adminfilters.filters import (
    ChoicesFieldComboFilter,
    RelatedFieldComboFilter,
    TextFieldFilter,
)

from ..utils.admin import HOPEModelAdminBase, LastSyncDateResetMixin
from .models import CashPlan, Program


@admin.register(Program)
class ProgramAdmin(LastSyncDateResetMixin, HOPEModelAdminBase):
    list_display = ("name", "status", "start_date", "end_date", "business_area")
    date_hierarchy = "start_date"
    list_filter = (
        ("status", ChoicesFieldComboFilter),
        ("business_area", RelatedFieldComboFilter),
        ("scope", ChoicesFieldComboFilter),
        "is_removed",
    )
    raw_id_fields = ("business_area",)
    filter_horizontal = ("admin_areas",)


@admin.register(CashPlan)
class CashPlanAdmin(HOPEModelAdminBase):
    list_display = ("name", "program", "delivery_type", "status")
    list_filter = (
        ("status", ChoicesFieldComboFilter),
        ("business_area", RelatedFieldComboFilter),
        ("delivery_type", ChoicesFieldComboFilter),
        TextFieldFilter.factory("program__id", "Program ID"),
        TextFieldFilter.factory("vision_id", "Vision ID"),
    )
    raw_id_fields = ("business_area",)
