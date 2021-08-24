from django.contrib import admin

from hct_mis_api.apps.activity_log.models import LogEntry


@admin.register(LogEntry)
class LogEntryAdmin(admin.ModelAdmin):
    list_display = (
        "timestamp",
        "user",
        "action",
        "business_area",
        "content_type",
    )
    date_hierarchy = "timestamp"
    search_fields = ("object_repr",)
    raw_id_fields = ("business_area", "user")
    list_filter = (
        "business_area",
        "content_type",
    )
