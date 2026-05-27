from admin_cursor_paginator import CursorPaginatorAdmin
from adminfilters.autocomplete import AutoCompleteFilter
from adminfilters.depot.widget import DepotManager
from adminfilters.filters import ChoicesFieldComboFilter, ValueFilter
from adminfilters.querystring import QueryStringFilter
from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest

from hope.admin.utils import HOPEModelAdminBase
from hope.models import PaymentVerification


@admin.register(PaymentVerification)
class PaymentVerificationAdmin(CursorPaginatorAdmin, HOPEModelAdminBase):
    list_display = (
        "payment",
        "household",
        "business_area",
        "status",
        "status_date",
        "received_amount",
        "payment_plan_name",
        "sent_to_rapid_pro",
    )

    list_filter = (
        (
            "payment_verification_plan__payment_plan__program_cycle__program__business_area",
            AutoCompleteFilter,
        ),
        (
            "payment_verification_plan__payment_plan__program_cycle__program",
            AutoCompleteFilter,
        ),
        DepotManager,
        QueryStringFilter,
        ("status", ChoicesFieldComboFilter),
        ("payment__household__unicef_id", ValueFilter),
        "sent_to_rapid_pro",
    )
    date_hierarchy = "updated_at"
    search_fields = ("payment__unicef_id",)

    def payment_plan_name(self, obj: PaymentVerification) -> str:  # pragma: no cover
        payment_plan = obj.payment_verification_plan.payment_plan
        return getattr(payment_plan, "name", "~no name~")

    def household(self, obj: PaymentVerification) -> str:  # pragma: no cover
        payment = obj.payment
        if payment and payment.household and payment.household.unicef_id:
            return payment.household.unicef_id
        return ""

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        return (
            super()
            .get_queryset(request)
            .select_related("payment_verification_plan")
            .prefetch_related(
                "payment",
                "payment__household",
                "payment_verification_plan__payment_plan",
                "payment_verification_plan__payment_plan__business_area",
            )
        )
