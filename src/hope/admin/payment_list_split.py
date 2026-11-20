from adminfilters.autocomplete import AutoCompleteFilter
from django.contrib import admin
from django.http import HttpRequest

from hope.admin.utils import HOPEModelAdminBase
from hope.models import PaymentListSplit


@admin.register(PaymentListSplit)
class PaymentListSplitAdmin(HOPEModelAdminBase):
    list_display = ("id", "payment_list", "split_type", "order", "sent_to_payment_gateway")
    list_filter = ("split_type", "sent_to_payment_gateway", ("payment_list", AutoCompleteFilter))
    search_fields = ("payment_list__unicef_id", "split_type")

    readonly_fields = [
        "id",
        "created_at",
        "updated_at",
        "payment_list",
        "split_type",
        "chunks_no",
        "sent_to_payment_gateway",
        "order",
    ]

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False
