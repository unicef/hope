from adminfilters.autocomplete import AutoCompleteFilter
from adminfilters.mixin import AdminFiltersMixin
from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from hope.admin.utils import AutocompleteForeignKeyMixin
from hope.models import WesternUnionPaymentPlanReport


@admin.register(WesternUnionPaymentPlanReport)
class WesternUnionPaymentPlanReportAdmin(AutocompleteForeignKeyMixin, AdminFiltersMixin, admin.ModelAdmin):
    list_display = ["id", "invoice", "payment_plan_admin_link", "sent"]
    list_filter = [("payment_plan", AutoCompleteFilter)]
    readonly_fields = ["download_link"]
    search_fields = ["invoice__name", "payment_plan__unicef_id", "payment_plan__name"]

    def payment_plan_admin_link(self, obj: WesternUnionPaymentPlanReport) -> str:
        url = reverse("admin:payment_paymentplan_change", args=[obj.payment_plan_id])
        return format_html('<a href="{}">{}</a>', url, obj.payment_plan)

    payment_plan_admin_link.short_description = "Payment Plan"

    def download_link(self, obj: WesternUnionPaymentPlanReport) -> str:  # pragma: no cover
        if not obj.report_file:
            return "-"
        return format_html('<a href="{}" target="_blank">Download</a>', obj.report_file.file.url)

    download_link.short_description = "File"
    download_link.admin_order_field = None
