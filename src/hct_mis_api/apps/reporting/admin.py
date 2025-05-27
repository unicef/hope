from adminfilters.autocomplete import AutoCompleteFilter
from adminfilters.mixin import AdminFiltersMixin
from django.contrib import admin

from hct_mis_api.apps.reporting.models import DashboardReport, Report


@admin.register(Report)
class ReportAdmin(AdminFiltersMixin, admin.ModelAdmin):
    list_display = (
        "report_type",
        "number_of_records",
        "business_area",
        "program",
        "status",
        "created_at",
        "date_from",
        "date_to",
    )
    raw_id_fields = ("business_area",)
    filter_horizontal = ["admin_area"]
    list_filter = (
        ("business_area", AutoCompleteFilter),
        ("program", AutoCompleteFilter),
        ("created_by", AutoCompleteFilter),
        "report_type",
        "status",
    )


@admin.register(DashboardReport)
class DashboardReportAdmin(AdminFiltersMixin, admin.ModelAdmin):
    list_display = ("report_type", "business_area", "program", "status", "created_at", "year")
    raw_id_fields = ("created_by", "program", "admin_area", "business_area")
    list_filter = (
        ("business_area", AutoCompleteFilter),
        ("program", AutoCompleteFilter),
        ("created_by", AutoCompleteFilter),
        "status",
        "year",
    )
