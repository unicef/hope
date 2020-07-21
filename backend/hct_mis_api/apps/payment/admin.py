from django.contrib import admin

from payment.models import PaymentRecord, CashPlanPaymentVerification


@admin.register(PaymentRecord)
class PaymentRecordAdmin(admin.ModelAdmin):
    pass


@admin.register(CashPlanPaymentVerification)
class CashPlanPaymentVerificationAdmin(admin.ModelAdmin):
    pass
