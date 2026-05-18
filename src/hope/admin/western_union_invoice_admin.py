from django.contrib import admin
from django.http import HttpRequest
from django.utils.html import format_html

from hope.admin.utils import AutocompleteForeignKeyMixin
from hope.models import WesternUnionInvoice, WesternUnionPaymentPlanReport


class WesternUnionPaymentPlanReportInline(AutocompleteForeignKeyMixin, admin.TabularInline):
    model = WesternUnionPaymentPlanReport
    extra = 0
    can_delete = False
    show_change_link = True
    readonly_fields = ["payment_plan", "sent", "report_file"]

    def has_add_permission(self, request: HttpRequest, obj: WesternUnionPaymentPlanReport | None = None) -> bool:
        return False


@admin.register(WesternUnionInvoice)
class WesternUnionInvoiceAdmin(AutocompleteForeignKeyMixin, admin.ModelAdmin):
    inlines = [WesternUnionPaymentPlanReportInline]
    list_display = [
        "name",
        "advice_name",
        "date",
        "net_amount",
        "charges",
        "status",
        "matched_data",
        "payment_plans_list",
    ]

    list_filter = ["status", "date"]
    search_fields = [
        "name",
        "advice_name",
        "matched_data__name",
        "reports__payment_plan__unicef_id",
        "reports__payment_plan__name",
    ]

    readonly_fields = ["download_link", "matched_data", "error_msg"]

    def download_link(self, obj: WesternUnionInvoice) -> str:  # pragma: no cover
        if not obj.file:
            return "-"
        return format_html('<a href="{}" target="_blank">Download</a>', obj.file.file.url)

    download_link.short_description = "File"
    download_link.admin_order_field = None

    def payment_plans_list(self, obj: WesternUnionInvoice) -> str:  # pragma: no cover
        return ", ".join(str(r.payment_plan) for r in obj.reports.all().select_related("payment_plan"))

    payment_plans_list.short_description = "Payment Plans"
