from django.contrib import admin

from payment.models import PaymentRecord


@admin.register(PaymentRecord)
class PaymentRecordAdmin(admin.ModelAdmin):
    pass
