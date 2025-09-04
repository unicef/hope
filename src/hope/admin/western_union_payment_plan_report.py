from django.contrib import admin
from django.utils.html import format_html

from hope.apps.payment.models import WesternUnionPaymentPlanReport


@admin.register(WesternUnionPaymentPlanReport)
class WesternUnionPaymentPlanReportAdmin(admin.ModelAdmin):
    list_display = ["id", "qcf_file", "payment_plan"]
    readonly_fields = ["download_link"]

    def download_link(self, obj: WesternUnionPaymentPlanReport) -> str:  # pragma: no cover
        if not obj.report_file:
            return "-"
        return format_html('<a href="{}" target="_blank">Download</a>', obj.report_file.file.url)

    download_link.short_description = "File"
    download_link.admin_order_field = None
