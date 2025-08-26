from typing import Any

from adminfilters.autocomplete import AutoCompleteFilter
from adminfilters.mixin import AdminFiltersMixin
from advanced_filters.admin import AdminAdvancedFiltersMixin
from django.contrib import admin
from django.db.models.query import QuerySet
from django.http import HttpRequest

from hope.models.activity_log import LogEntry


@admin.register(LogEntry)
class LogEntryAdmin(AdminAdvancedFiltersMixin, AdminFiltersMixin, admin.ModelAdmin):
    list_display = (
        "timestamp",
        "business_area",
        "user",
        "action",
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
    filter_horizontal = ("programs",)
    readonly_fields = [field.name for field in LogEntry._meta.get_fields()]

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False

    def has_delete_permission(self, request: HttpRequest, obj: Any | None = None) -> bool:
        return False

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        return super().get_queryset(request).select_related("content_type", "user", "business_area")
