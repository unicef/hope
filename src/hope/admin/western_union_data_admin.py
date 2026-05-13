from django.contrib import admin
from django.utils.html import format_html

from hope.admin.utils import AutocompleteForeignKeyMixin
from hope.models import WesternUnionData


@admin.register(WesternUnionData)
class WesternUnionDataAdmin(AutocompleteForeignKeyMixin, admin.ModelAdmin):
    list_display = ["name", "date", "amount", "status", "matched_invoices_list"]
    list_filter = ["status", "date"]
    search_fields = ["name", "matched_invoices__name"]
    readonly_fields = ["download_link", "error_msg"]

    def download_link(self, obj: WesternUnionData) -> str:
        if not obj.file:
            return "-"
        return format_html('<a href="{}" target="_blank">Download</a>', obj.file.file.url)

    download_link.short_description = "File"
    download_link.admin_order_field = None

    def matched_invoices_list(self, obj: WesternUnionData) -> str:
        return ", ".join(obj.matched_invoices.values_list("name", flat=True))

    matched_invoices_list.short_description = "Matched Invoices"
