from adminfilters.autocomplete import AutoCompleteFilter
from adminfilters.mixin import AdminFiltersMixin
from django.contrib import admin
from django.http import HttpRequest
from django.urls import reverse
from django.utils.html import format_html

from hope.admin.utils import AutocompleteForeignKeyMixin
from hope.models import WesternUnionPaymentListReport


@admin.register(WesternUnionPaymentListReport)
class WesternUnionPaymentListReportAdmin(AutocompleteForeignKeyMixin, AdminFiltersMixin, admin.ModelAdmin):
    list_display = ["id", "invoice", "payment_list_admin_link", "sent"]
    list_filter = [("payment_list", AutoCompleteFilter)]
    search_fields = ["invoice__name", "payment_list__unicef_id", "payment_list__name"]
    readonly_fields = ["id", "invoice", "report_file", "payment_list"]

    def payment_list_admin_link(self, obj: WesternUnionPaymentListReport) -> str:
        url = reverse("admin:payment_paymentlist_change", args=[obj.payment_list_id])
        return format_html('<a href="{}">{}</a>', url, obj.payment_list)

    payment_list_admin_link.short_description = "Payment List"

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False
