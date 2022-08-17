from django.contrib import admin

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
    raw_id_fields = ("business_area", "user")
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
