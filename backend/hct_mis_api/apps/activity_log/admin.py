from django.contrib import admin
from django.contrib.admin import ChoicesFieldListFilter, RelatedFieldListFilter

from adminfilters.autocomplete import AutoCompleteFilter
from adminfilters.filters import RelatedFieldComboFilter

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
        "action",
        ("user", AutoCompleteFilter),
        ("business_area", AutoCompleteFilter),
        ("content_type", RelatedFieldComboFilter),
    )
