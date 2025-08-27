from typing import Any

from adminfilters.autocomplete import AutoCompleteFilter
from django.contrib import admin
from django.http import HttpRequest
from smart_admin.modeladmin import SmartModelAdmin

from hope.models.api_log_entry import APILogEntry


@admin.register(APILogEntry)
class APILogEntryAdmin(SmartModelAdmin):
    list_display = ("token", "url", "method", "timestamp")
    list_filter = (("token", AutoCompleteFilter), "method")
    date_hierarchy = "timestamp"
    search_fields = "url"

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False

    def has_change_permission(self, request: HttpRequest, obj: Any | None = None) -> bool:
        return False
