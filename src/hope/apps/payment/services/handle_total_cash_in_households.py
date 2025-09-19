from uuid import UUID

from django.db.models import F, OuterRef, Subquery, Sum
from django.db.models.functions import Coalesce

from hope.models.household import Household
from hope.models.payment import Payment


def handle_total_cash_in_specific_households(id_list: list[UUID]) -> None:
    total_cash_received_payment_subquery = Subquery(
        Payment.objects.filter(status__in=Payment.DELIVERED_STATUSES, household__pk=OuterRef("pk"))
        .values("household__pk")
        .annotate(sum_delivered_quantity=Sum("delivered_quantity"))
        .values("sum_delivered_quantity")[:1]
    )
    total_cash_received_usd_payment_subquery = Subquery(
        Payment.objects.filter(status__in=Payment.DELIVERED_STATUSES, household__pk=OuterRef("pk"))
        .values("household__pk")
        .annotate(sum_delivered_quantity_usd=Sum("delivered_quantity_usd"))
        .values("sum_delivered_quantity_usd")[:1]
    )
    Household.objects.filter(id__in=id_list).annotate(
        total_cash_received_from_payments=Coalesce(total_cash_received_payment_subquery, 0),
        total_cash_received_from_payments_usd=Coalesce(total_cash_received_usd_payment_subquery, 0),
    ).update(
        total_cash_received=F("total_cash_received_from_payments"),
        total_cash_received_usd=F("total_cash_received_from_payments_usd"),
    )
