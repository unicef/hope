from adminfilters.autocomplete import AutoCompleteFilter
from django.contrib import admin

from hope.admin.utils import HOPEModelAdminBase
from hope.contrib.vision.models import FundsCommitmentItem


@admin.register(FundsCommitmentItem)
class FundsCommitmentItemAdmin(HOPEModelAdminBase):
    list_display = (
        "rec_serial_number",
        "funds_commitment_group",
        "funds_commitment_item",
        "office",
        "fc_status",
        "get_fund_display",
        "wbs_element",
        "grant_number",
    )
    list_filter = (
        ("office", AutoCompleteFilter),
        ("funds_commitment_group", AutoCompleteFilter),
    )
    search_fields = (
        "rec_serial_number",
        "funds_commitment_group__funds_commitment_number",
        "funds_commitment_item",
        "wbs_element",
        "grant_number",
    )
