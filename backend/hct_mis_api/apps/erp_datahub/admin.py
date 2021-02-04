# Register your models here.
from django.contrib import admin

from hct_mis_api.apps.erp_datahub.models import FundsCommitment, DownPayment


@admin.register(FundsCommitment)
class FundsCommitmentAdmin(admin.ModelAdmin):
    pass


@admin.register(DownPayment)
class DownPaymentAdmin(admin.ModelAdmin):
    pass
