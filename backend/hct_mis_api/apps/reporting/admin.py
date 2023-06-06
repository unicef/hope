from django.contrib import admin

from hct_mis_api.apps.reporting.models import DashboardReport, Report


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ("report_type", "number_of_records", "business_area", "status", "created_at", "date_from", "date_to")


@admin.register(DashboardReport)
class DashboardReportAdmin(admin.ModelAdmin):
    list_display = ("report_type", "business_area", "status", "created_at", "year")
