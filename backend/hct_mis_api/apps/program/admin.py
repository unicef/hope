from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest

from adminfilters.autocomplete import AutoCompleteFilter
from adminfilters.dates import DateRangeFilter
from adminfilters.filters import ChoicesFieldComboFilter
from adminfilters.mixin import AdminAutoCompleteSearchMixin

from hct_mis_api.apps.program.models import Program, ProgramCycle
from hct_mis_api.apps.utils.admin import (
    HOPEModelAdminBase,
    LastSyncDateResetMixin,
    SoftDeletableAdminMixin,
)


@admin.register(ProgramCycle)
class ProgramCycleAdmin(SoftDeletableAdminMixin, LastSyncDateResetMixin, HOPEModelAdminBase):
    list_display = ("program", "iteration", "status", "start_date", "end_date")
    # date_hierarchy = "program__start_date"
    list_filter = (
        ("status", ChoicesFieldComboFilter),
        ("program__start_date", DateRangeFilter),
    )
    raw_id_fields = ("program",)

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        return ProgramCycle.all_objects.select_related("program")
        # return super().get_queryset(request).select_related("program")


class ProgramCycleAdminInline(admin.TabularInline):
    model = ProgramCycle
    extra = 0
    readonly_fields = (
        "created_at",
        "updated_at",
    )


@admin.register(Program)
class ProgramAdmin(SoftDeletableAdminMixin, AdminAutoCompleteSearchMixin, LastSyncDateResetMixin, HOPEModelAdminBase):
    list_display = (
        "name",
        "status",
        "start_date",
        "end_date",
        "business_area",
        "data_collecting_type",
        "is_visible",
    )
    date_hierarchy = "start_date"
    search_fields = ("name",)
    list_filter = (
        ("status", ChoicesFieldComboFilter),
        ("business_area", AutoCompleteFilter),
        ("scope", ChoicesFieldComboFilter),
        "is_visible",
    )
    raw_id_fields = ("business_area", "data_collecting_type")
    filter_horizontal = ("admin_areas",)

    inlines = (ProgramCycleAdminInline,)
    ordering = ("name",)

    # def get_queryset(self, request: HttpRequest) -> QuerySet:
    #     return super().get_queryset(request).select_related("data_collecting_type", "business_area")
