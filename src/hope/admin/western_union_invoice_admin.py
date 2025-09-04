
from django.contrib import admin
from django.http import HttpRequest
from django.utils.html import format_html

from hope.apps.payment.models import WesternUnionInvoice, WesternUnionPaymentPlanReport


class WesternUnionPaymentPlanReportInline(admin.TabularInline):
    model = WesternUnionPaymentPlanReport
    extra = 0
    can_delete = False
    show_change_link = True
    readonly_fields = ["payment_plan", "sent", "report_file"]

    def has_add_permission(self, request: HttpRequest, obj: WesternUnionPaymentPlanReport | None = None) -> bool:
        return False


@admin.register(WesternUnionInvoice)
class WesternUnionInvoiceAdmin(admin.ModelAdmin):
    inlines = [WesternUnionPaymentPlanReportInline]
    list_display = ["name", "payment_plans_list"]

    search_fields = ["name", "reports__payment_plan__unicef_id", "reports__payment_plan__name"]

    readonly_fields = ["download_link"]

    def download_link(self, obj: WesternUnionInvoice) -> str:  # pragma: no cover
        if not obj.file:
            return "-"
        return format_html('<a href="{}" target="_blank">Download</a>', obj.file.file.url)

    download_link.short_description = "File"
    download_link.admin_order_field = None

    def payment_plans_list(self, obj: WesternUnionInvoice) -> str:  # pragma: no cover
        return ", ".join(str(r.payment_plan) for r in obj.reports.all().select_related("payment_plan"))

    payment_plans_list.short_description = "Payment Plans"
