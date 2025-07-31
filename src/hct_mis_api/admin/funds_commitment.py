from django.contrib import admin

from adminfilters.filters import ValueFilter

from hct_mis_api.admin.utils import HOPEModelAdminBase
from hct_mis_api.contrib.vision.models import (
    FundsCommitment,
)


@admin.register(FundsCommitment)
class FundsCommitmentAdmin(HOPEModelAdminBase):
    list_display = (
        "rec_serial_number",
        "business_area",
        "funds_commitment_item",
        "funds_commitment_number",
        "posting_date",
        "grant_number",
        "wbs_element",
    )
    list_filter = (
        "business_area",
        "posting_date",
        ("business_area", ValueFilter),
    )
    search_fields = (
        "rec_serial_number",
        "vendor_id",
        "wbs_element",
        "funds_commitment_number",
        "grant_number",
        "wbs_element",
    )
