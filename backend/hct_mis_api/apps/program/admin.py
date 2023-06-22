from django.contrib import admin

from adminfilters.autocomplete import AutoCompleteFilter
from adminfilters.filters import ChoicesFieldComboFilter

from hct_mis_api.apps.program.models import Program, ProgramCycle
from hct_mis_api.apps.utils.admin import (
    HOPEModelAdminBase,
    LastSyncDateResetMixin,
    SoftDeletableAdminMixin,
)


@admin.register(ProgramCycle)
class ProgramCycleAdmin(SoftDeletableAdminMixin, LastSyncDateResetMixin, HOPEModelAdminBase):
    list_display = ("program", "iteration", "status", "start_date", "end_date")
    date_hierarchy = "program__start_date"
    list_filter = (("status", ChoicesFieldComboFilter),)


class ProgramCycleAdminInline(admin.TabularInline):
    model = ProgramCycle
    extra = 0
    readonly_fields = (
        "created_at",
        "updated_at",
    )


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

    inlines = (ProgramCycleAdminInline,)
