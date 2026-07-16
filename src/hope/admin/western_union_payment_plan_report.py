from typing import Any

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
    search_fields = ["invoice__name", "payment_plan__unicef_id", "payment_plan__name"]
    readonly_fields = ["id", "invoice", "report_file", "payment_plan"]

    def payment_plan_admin_link(self, obj: WesternUnionPaymentPlanReport) -> str:
        url = reverse("admin:payment_paymentplan_change", args=[obj.payment_plan_id])
        return format_html('<a href="{}">{}</a>', url, obj.payment_plan)

    payment_plan_admin_link.short_description = "Payment Plan"

    def has_add_permission(self: Any, request: Any, obj: Any = None) -> bool:
        return False
