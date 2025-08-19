from adminfilters.autocomplete import AutoCompleteFilter
from django.contrib import admin

from hope.admin.utils import HOPEModelAdminBase
from hope.contrib.vision.models import FundsCommitmentItem


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
