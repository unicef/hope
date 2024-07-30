from typing import Optional

from django.contrib import admin
from django.http import HttpRequest

from adminfilters.autocomplete import LinkedAutoCompleteFilter
from adminfilters.combo import ChoicesFieldComboFilter

from hct_mis_api.apps.periodic_data_update.models import (
    PeriodicDataUpdateTemplate,
    PeriodicDataUpdateUpload,
)
from hct_mis_api.apps.utils.admin import HOPEModelAdminBase


class PeriodicDataUpdateUploadInline(admin.TabularInline):
    model = PeriodicDataUpdateUpload
    extra = 0
    show_change_link = True
    can_add = False
    fields = ("id", "status", "created_by", "created_at")
    readonly_fields = fields

    def has_add_permission(self, request: HttpRequest, obj: Optional[PeriodicDataUpdateUpload] = None) -> bool:
        return False


@admin.register(PeriodicDataUpdateTemplate)
class PeriodicDataUpdateTemplateAdmin(HOPEModelAdminBase):
    list_display = ("id", "status", "program", "created_by", "created_at")
    list_filter = (
        ("business_area", LinkedAutoCompleteFilter.factory(parent=None)),
        ("program", LinkedAutoCompleteFilter.factory(parent="business_area")),
        ("status", ChoicesFieldComboFilter),
    )
    inlines = [PeriodicDataUpdateUploadInline]


@admin.register(PeriodicDataUpdateUpload)
class PeriodicDataUpdateUploadAdmin(HOPEModelAdminBase):
    list_display = ("id", "status", "template", "created_by", "created_at")
    list_filter = (("status", ChoicesFieldComboFilter),)
