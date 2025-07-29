from django.contrib import admin

from adminfilters.autocomplete import AutoCompleteFilter

from hct_mis_api.admin.utils_admin import HOPEModelAdminBase
from hct_mis_api.contrib.vision.models import (
    FundsCommitmentItem,
)


@admin.register(FundsCommitmentItem)
class FundsCommitmentItemAdmin(HOPEModelAdminBase):
    list_display = (
        "rec_serial_number",
        "business_area",
        "office",
        "funds_commitment_item",
        "funds_commitment_group",
    )
    list_filter = (
        ("office", AutoCompleteFilter),
        ("funds_commitment_group", AutoCompleteFilter),
    )
    search_fields = (
        "rec_serial_number",
        "funds_commitment_number",
        "funds_commitment_item",
    )
