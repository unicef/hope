from django.contrib import admin

from adminfilters.filters import ValueFilter

from hct_mis_api.apps.utils.admin import HOPEModelAdminBase
from hct_mis_api.contrib.vision.models import DownPayment, FundsCommitment


@admin.register(FundsCommitment)
class FundsCommitmentAdmin(HOPEModelAdminBase):
    list_display = (
        "rec_serial_number",
        "business_area",
        "funds_commitment_item",
        "funds_commitment_number",
        "posting_date",
    )
    list_filter = (
        "business_area",
        "posting_date",
        ("business_area", ValueFilter),
    )
    search_fields = ("rec_serial_number", "vendor_id", "wbs_element", "funds_commitment_number")


@admin.register(DownPayment)
class DownPaymentAdmin(HOPEModelAdminBase):
    list_display = ("rec_serial_number", "down_payment_reference", "business_area", "consumed_fc_number")

    list_filter = (("business_area", ValueFilter),)
