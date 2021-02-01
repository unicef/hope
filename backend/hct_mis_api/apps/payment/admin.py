from adminfilters.filters import ChoicesFieldComboFilter
from django.contrib import admin

from hct_mis_api.apps.payment.models import PaymentRecord, CashPlanPaymentVerification, PaymentVerification
from hct_mis_api.apps.utils.admin import HOPEModelAdminBase


@admin.register(PaymentRecord)
class PaymentRecordAdmin(HOPEModelAdminBase):
    list_filter = (('status', ChoicesFieldComboFilter),
                   )
    date_hierarchy = 'updated_at'

@admin.register(CashPlanPaymentVerification)
class CashPlanPaymentVerificationAdmin(HOPEModelAdminBase):
    list_filter = (('status', ChoicesFieldComboFilter),
                   )
    date_hierarchy = 'updated_at'


@admin.register(PaymentVerification)
class PaymentVerificationAdmin(HOPEModelAdminBase):
    list_filter = (('status', ChoicesFieldComboFilter),
                   )
    date_hierarchy = 'updated_at'
