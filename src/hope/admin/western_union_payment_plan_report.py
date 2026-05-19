from adminfilters.autocomplete import AutoCompleteFilter
from adminfilters.mixin import AdminFiltersMixin
from django.contrib import admin
from django.forms import ModelForm
from django.utils.html import format_html

from hope.admin.utils import AutocompleteForeignKeyMixin
from hope.models import WesternUnionPaymentPlanReport


class WesternUnionPaymentPlanReportAdminForm(ModelForm):
    class Meta:
        model = WesternUnionPaymentPlanReport
        fields = ["qcf_file", "report_file", "payment_plan", "sent"]
        labels = {"qcf_file": "Invoice"}


@admin.register(WesternUnionPaymentPlanReport)
class WesternUnionPaymentPlanReportAdmin(AutocompleteForeignKeyMixin, AdminFiltersMixin, admin.ModelAdmin):
    form = WesternUnionPaymentPlanReportAdminForm
    list_display = ["id", "invoice", "payment_plan"]
    list_filter = [("payment_plan", AutoCompleteFilter)]
    readonly_fields = ["download_link"]

    def invoice(self, obj: WesternUnionPaymentPlanReport) -> str:
        return str(obj.qcf_file)

    invoice.short_description = "Invoice"
    invoice.admin_order_field = "qcf_file"

    def download_link(self, obj: WesternUnionPaymentPlanReport) -> str:  # pragma: no cover
        if not obj.report_file:
            return "-"
        return format_html('<a href="{}" target="_blank">Download</a>', obj.report_file.file.url)

    download_link.short_description = "File"
    download_link.admin_order_field = None
