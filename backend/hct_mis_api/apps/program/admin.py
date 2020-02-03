from django.contrib import admin

from .models import Program, CashPlan


@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ("name", "status", "start_date", "end_date", "business_area")


@admin.register(CashPlan)
class CashPlanAdmin(admin.ModelAdmin):
    pass
