from django.contrib import admin
from django.http import HttpRequest

from hope.admin.utils import AutocompleteForeignKeyMixin
from hope.models import WesternUnionData


@admin.register(WesternUnionData)
class WesternUnionDataAdmin(AutocompleteForeignKeyMixin, admin.ModelAdmin):
    list_display = ["name", "date", "amount", "status", "matched_invoices_list"]
    list_filter = ["status", "date"]
    search_fields = ["name", "matched_invoices__name"]
    readonly_fields = ["id", "name", "date", "file", "amount", "error_msg"]

    def matched_invoices_list(self, obj: WesternUnionData) -> str:
        return ", ".join(obj.matched_invoices.values_list("name", flat=True))

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False

    matched_invoices_list.short_description = "Matched Invoices"
