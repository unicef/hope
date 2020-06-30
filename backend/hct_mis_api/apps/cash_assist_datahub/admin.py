# Register your models here.
from django.contrib import admin

from cash_assist_datahub.models import (
    CashPlan,
    Session,
    TargetPopulation,
    Programme,
    ServiceProvider,
    PaymentRecord,
)


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    pass


@admin.register(CashPlan)
class CashPlanAdmin(admin.ModelAdmin):
    pass


@admin.register(PaymentRecord)
class CashPlanAdmin(admin.ModelAdmin):
    pass


@admin.register(ServiceProvider)
class CashPlanAdmin(admin.ModelAdmin):
    pass


@admin.register(Programme)
class CashPlanAdmin(admin.ModelAdmin):
    pass


@admin.register(TargetPopulation)
class CashPlanAdmin(admin.ModelAdmin):
    pass
