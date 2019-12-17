from django.contrib import admin

from .models import Program, CashPlan


class ProgramAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'start_date', 'end_date', 'location')


admin.site.register(Program, ProgramAdmin)
admin.site.register(CashPlan)
