from typing import Any, Optional

from django.contrib import admin
from django.http import HttpRequest

from adminfilters.autocomplete import AutoCompleteFilter
from adminfilters.mixin import AdminFiltersMixin
from advanced_filters.admin import AdminAdvancedFiltersMixin

from hct_mis_api.apps.activity_log.models import LogEntry


@admin.register(LogEntry)
class LogEntryAdmin(AdminAdvancedFiltersMixin, AdminFiltersMixin, admin.ModelAdmin):
    list_display = (
        "timestamp",
        "user",
        "action",
        "business_area",
        "content_type",
    )
    date_hierarchy = "timestamp"
    search_fields = ("object_repr", "object_id")
    list_filter = (
        "action",
        ("user", AutoCompleteFilter),
        ("business_area", AutoCompleteFilter),
        ("content_type", AutoCompleteFilter),
    )
    advanced_filter_fields = (
        "action",
        "user",
        "content_type",
    )
    readonly_fields = [field.name for field in LogEntry._meta.get_fields()]

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False

    def has_delete_permission(self, request: HttpRequest, obj: Optional[Any] = None) -> bool:
        return False
