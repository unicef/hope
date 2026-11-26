from django.contrib import admin
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.html import format_html

from hope.admin.utils import AutocompleteForeignKeyMixin
from hope.models import WesternUnionInvoice, WesternUnionPaymentListReport


class WesternUnionPaymentListReportInline(AutocompleteForeignKeyMixin, admin.TabularInline):
    model = WesternUnionPaymentListReport
    extra = 0
    can_delete = False
    show_change_link = True
    fields = ["report_admin_link", "payment_list_admin_link", "sent"]
    readonly_fields = ["report_admin_link", "payment_list_admin_link", "sent"]

    def report_admin_link(self, obj: WesternUnionPaymentListReport) -> str:
        url = reverse("admin:payment_westernunionpaymentlistreport_change", args=[obj.pk])
        return format_html('<a href="{}">Report #{}</a>', url, obj.pk)

    report_admin_link.short_description = "Report"

    def payment_list_admin_link(self, obj: WesternUnionPaymentListReport) -> str:
        url = reverse("admin:payment_paymentlist_change", args=[obj.payment_list_id])
        return format_html('<a href="{}">{}</a>', url, obj.payment_list)

    payment_list_admin_link.short_description = "Payment List"

    def has_add_permission(self, request: HttpRequest, obj: WesternUnionPaymentListReport | None = None) -> bool:
        return False


@admin.register(WesternUnionInvoice)
class WesternUnionInvoiceAdmin(AutocompleteForeignKeyMixin, admin.ModelAdmin):
    LEGACY_FILTER_PARAM = "is_legacy__exact"

    inlines = [WesternUnionPaymentListReportInline]
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
        "reports__payment_list__unicef_id",
        "reports__payment_list__name",
    ]

    readonly_fields = [
        "id",
        "name",
        "is_legacy",
        "date",
        "file",
        "advice_name",
        "matched_data",
        "net_amount",
        "charges",
        "error_msg",
    ]

    def changelist_view(self, request: HttpRequest, extra_context: dict[str, object] | None = None) -> HttpResponse:
        if self.LEGACY_FILTER_PARAM not in request.GET:
            query_params = request.GET.copy()
            query_params[self.LEGACY_FILTER_PARAM] = "0"
            return redirect(f"{request.path}?{query_params.urlencode()}")
        return super().changelist_view(request, extra_context)

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False
