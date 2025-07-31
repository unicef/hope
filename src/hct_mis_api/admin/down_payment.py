from django.contrib import admin

from adminfilters.filters import ValueFilter

from hct_mis_api.admin.utils import HOPEModelAdminBase
from hct_mis_api.contrib.vision.models import (
    DownPayment,
)


@admin.register(DownPayment)
class DownPaymentAdmin(HOPEModelAdminBase):
    list_display = ("rec_serial_number", "down_payment_reference", "business_area", "consumed_fc_number", "doc_number")

    list_filter = (("business_area", ValueFilter), "doc_number")
