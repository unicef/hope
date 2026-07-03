from django.contrib import admin
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.html import format_html

from hope.admin.utils import AutocompleteForeignKeyMixin
from hope.models import WesternUnionInvoice, WesternUnionPaymentPlanReport


class WesternUnionPaymentPlanReportInline(AutocompleteForeignKeyMixin, admin.TabularInline):
    model = WesternUnionPaymentPlanReport
    extra = 0
    can_delete = False
    show_change_link = True
    fields = ["report_admin_link", "payment_plan_admin_link", "sent"]
    readonly_fields = ["report_admin_link", "payment_plan_admin_link", "sent"]

    def report_admin_link(self, obj: WesternUnionPaymentPlanReport) -> str:
        url = reverse("admin:payment_westernunionpaymentplanreport_change", args=[obj.pk])
        return format_html('<a href="{}">Report #{}</a>', url, obj.pk)

    report_admin_link.short_description = "Report"

    def payment_plan_admin_link(self, obj: WesternUnionPaymentPlanReport) -> str:
        url = reverse("admin:payment_paymentplan_change", args=[obj.payment_plan_id])
        return format_html('<a href="{}">{}</a>', url, obj.payment_plan)

    payment_plan_admin_link.short_description = "Payment Plan"

    def has_add_permission(self, request: HttpRequest, obj: WesternUnionPaymentPlanReport | None = None) -> bool:
        return False


@admin.register(WesternUnionInvoice)
class WesternUnionInvoiceAdmin(AutocompleteForeignKeyMixin, admin.ModelAdmin):
    LEGACY_FILTER_PARAM = "is_legacy__exact"

    inlines = [WesternUnionPaymentPlanReportInline]
    list_display = [
        "name",
        "advice_name",
        "date",
        "net_amount",
        "charges",
        "status",
        "matched_data",
    ]

    list_filter = ["is_legacy", "status", "date"]
    search_fields = [
        "name",
        "advice_name",
        "matched_data__name",
        "reports__payment_plan__unicef_id",
        "reports__payment_plan__name",
    ]

    readonly_fields = ["download_link", "matched_data", "error_msg"]

    def changelist_view(self, request: HttpRequest, extra_context: dict[str, object] | None = None) -> HttpResponse:
        if self.LEGACY_FILTER_PARAM not in request.GET:
            query_params = request.GET.copy()
            query_params[self.LEGACY_FILTER_PARAM] = "0"
            return redirect(f"{request.path}?{query_params.urlencode()}")
        return super().changelist_view(request, extra_context)

    def download_link(self, obj: WesternUnionInvoice) -> str:  # pragma: no cover
        if not obj.file:
            return "-"
        return format_html('<a href="{}" target="_blank">Download</a>', obj.file.file.url)

    download_link.short_description = "File"
    download_link.admin_order_field = None
