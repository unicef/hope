from adminfilters.autocomplete import AutoCompleteFilter
from adminfilters.filters import ForeignKeyFieldFilter
from advanced_filters.admin import AdminAdvancedFiltersMixin
from smart_admin.logs.admin import LogEntryAdmin as SmartLogEntryAdmin


class LogEntryAdmin(AdminAdvancedFiltersMixin, SmartLogEntryAdmin):
    list_display = (
        "action_time",
        "user",
        "action_flag",
        "content_type",
        "object_repr",
        "object_id",
    )

    advanced_filter_fields = (
        "content_type",
        "user",
    )
    search_fields = ("object_repr",)
    list_filter = (
        ("user", AutoCompleteFilter),
        ("content_type", AutoCompleteFilter),
        ForeignKeyFieldFilter.factory("object_id"),
        "action_time",
        "action_flag",
    )
