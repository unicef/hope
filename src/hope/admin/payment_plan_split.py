from typing import Any

from adminfilters.autocomplete import AutoCompleteFilter
from django.contrib import admin

from hope.admin.utils import HOPEModelAdminBase
from hope.models import PaymentPlanSplit


@admin.register(PaymentPlanSplit)
class PaymentPlanSplitAdmin(HOPEModelAdminBase):
    list_display = ("id", "payment_plan", "split_type", "order", "sent_to_payment_gateway")
    list_filter = ("split_type", "sent_to_payment_gateway", ("payment_plan", AutoCompleteFilter))
    search_fields = ("payment_plan__unicef_id", "split_type")

    readonly_fields = [
        "id",
        "created_at",
        "updated_at",
        "payment_plan",
        "split_type",
        "chunks_no",
        "sent_to_payment_gateway",
        "order",
    ]

    def has_add_permission(self: Any, request: Any, obj: Any = None) -> bool:
        return False
