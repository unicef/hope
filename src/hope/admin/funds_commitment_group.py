from django.contrib import admin
from django.http import HttpRequest

from hope.admin.utils import HOPEModelAdminBase
from hope.contrib.vision.models import FundsCommitmentGroup, FundsCommitmentItem


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

    def has_add_permission(self, request: HttpRequest, obj: FundsCommitmentGroup | None = None) -> bool:
        return False

    def has_change_permission(self, request: HttpRequest, obj: FundsCommitmentGroup | None = None) -> bool:
        return False

    def has_delete_permission(self, request: HttpRequest, obj: FundsCommitmentGroup | None = None) -> bool:
        return False


@admin.register(FundsCommitmentGroup)
class FundsCommitmentGroupAdmin(HOPEModelAdminBase):
    list_display = ("funds_commitment_number",)
    search_fields = ("funds_commitment_number",)
    inlines = (FundsCommitmentItemInline,)
