from django.contrib import admin

from adminfilters.autocomplete import AutoCompleteFilter
from adminfilters.filters import ValueFilter

from hct_mis_api.apps.utils.admin import HOPEModelAdminBase
from hct_mis_api.contrib.vision.models import (
    DownPayment,
    FundsCommitment,
    FundsCommitmentItem,
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


@admin.register(DownPayment)
class DownPaymentAdmin(HOPEModelAdminBase):
    list_display = ("rec_serial_number", "down_payment_reference", "business_area", "consumed_fc_number", "doc_number")

    list_filter = (("business_area", ValueFilter), "doc_number")


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
