from decimal import Decimal
from typing import cast

from django.contrib import admin
from django.http import HttpRequest

from hope.admin.utils import HOPEModelAdminBase
from hope.contrib.vision.models import (
    FundsCommitmentHeader,
    FundsCommitmentHeaderQuerySet,
    FundsCommitmentItem,
)


class FundsCommitmentItemInline(admin.TabularInline):
    model = FundsCommitmentItem
    extra = 0
    can_delete = False
    fields = readonly_fields = (
        "rec_serial_number",
        "funds_commitment_item",
        "office",
        "fc_status",
        "commitment_amount_local",
        "commitment_amount_usd",
        "total_open_amount_local",
        "total_open_amount_usd",
    )

    def has_add_permission(self, request: HttpRequest, obj: FundsCommitmentHeader | None = None) -> bool:
        return False

    def has_change_permission(self, request: HttpRequest, obj: FundsCommitmentHeader | None = None) -> bool:
        return False

    def has_delete_permission(self, request: HttpRequest, obj: FundsCommitmentHeader | None = None) -> bool:
        return False


@admin.register(FundsCommitmentHeader)
class FundsCommitmentHeaderAdmin(HOPEModelAdminBase):
    list_display = (
        "funds_commitment_number",
        "vendor_id",
        "posting_date",
        "document_reference",
        "fc_status",
        "total_amount_usd",
        "total_amount_local",
        "currency",
    )
    readonly_fields = (
        "vendor_id",
        "posting_date",
        "document_reference",
        "fc_status",
        "total_amount_usd",
        "total_amount_local",
        "currency",
    )
    search_fields = ("funds_commitment_number",)
    inlines = (FundsCommitmentItemInline,)

    def get_queryset(self, request: HttpRequest) -> FundsCommitmentHeaderQuerySet:
        return cast("FundsCommitmentHeaderQuerySet", super().get_queryset(request)).with_derived_fields()

    @admin.display(ordering="total_amount_usd", description="Total Amount USD")
    def total_amount_usd(self, obj: FundsCommitmentHeader) -> Decimal | None:
        return cast("Decimal | None", getattr(obj, "total_amount_usd", None))

    @admin.display(ordering="total_amount_local", description="Total Amount Local")
    def total_amount_local(self, obj: FundsCommitmentHeader) -> Decimal | None:
        return cast("Decimal | None", getattr(obj, "total_amount_local", None))
