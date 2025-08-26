from adminfilters.autocomplete import AutoCompleteFilter, LinkedAutoCompleteFilter
from adminfilters.combo import ChoicesFieldComboFilter
from django.contrib import admin
from django.db.models.query import QuerySet
from django.http import HttpRequest

from hope.admin.utils import HOPEModelAdminBase
from hope.models.periodic_data_update_template import (
    PeriodicDataUpdateTemplate,
)
from hope.models.periodic_data_update_update import PeriodicDataUpdateUpload


class PeriodicDataUpdateUploadInline(admin.TabularInline):
    model = PeriodicDataUpdateUpload
    extra = 0
    show_change_link = True
    can_add = False
    fields = ("id", "status", "created_by", "created_at")
    readonly_fields = fields

    def has_add_permission(self, request: HttpRequest, obj: PeriodicDataUpdateUpload | None = None) -> bool:
        return False


@admin.register(PeriodicDataUpdateTemplate)
class PeriodicDataUpdateTemplateAdmin(HOPEModelAdminBase):
    list_display = (
        "id",
        "status",
        "business_area",
        "program",
        "created_by",
        "created_at",
    )
    list_filter = (
        ("business_area", LinkedAutoCompleteFilter.factory(parent=None)),
        ("program", LinkedAutoCompleteFilter.factory(parent="business_area")),
        ("status", ChoicesFieldComboFilter),
        ("created_by", AutoCompleteFilter),
    )
    raw_id_fields = ("file", "program", "business_area", "created_by")
    inlines = [PeriodicDataUpdateUploadInline]

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        return super().get_queryset(request).select_related("created_by", "program", "business_area")


@admin.register(PeriodicDataUpdateUpload)
class PeriodicDataUpdateUploadAdmin(HOPEModelAdminBase):
    list_display = ("id", "status", "template", "created_by", "created_at")
    list_filter = (
        ("status", ChoicesFieldComboFilter),
        ("created_by", AutoCompleteFilter),
    )

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        return (
            super()
            .get_queryset(request)
            .select_related(
                "created_by",
                "template",
            )
        )
