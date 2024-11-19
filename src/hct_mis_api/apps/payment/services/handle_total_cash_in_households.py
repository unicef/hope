from typing import List
from uuid import UUID

from django.db.models import F, OuterRef, Subquery, Sum
from django.db.models.functions import Coalesce

from hct_mis_api.apps.household.models import Household
from hct_mis_api.apps.payment.models import Payment, PaymentRecord


def handle_total_cash_in_specific_households(id_list: List[UUID]) -> None:
    total_cash_received_payment_record_subquery = Subquery(
        PaymentRecord.objects.filter(household__pk=OuterRef("pk"))
        .values("household__pk")
        .annotate(sum_delivered_quantity=Sum("delivered_quantity"))
        .values("sum_delivered_quantity")[:1]
    )
    total_cash_received_usd_payment_record_subquery = Subquery(
        PaymentRecord.objects.filter(household__pk=OuterRef("pk"))
        .values("household__pk")
        .annotate(sum_delivered_quantity_usd=Sum("delivered_quantity_usd"))
        .values("sum_delivered_quantity_usd")[:1]
    )
    total_cash_received_payment_subquery = Subquery(
        Payment.objects.filter(status__in=Payment.ALLOW_CREATE_VERIFICATION, household__pk=OuterRef("pk"))
        .values("household__pk")
        .annotate(sum_delivered_quantity=Sum("delivered_quantity"))
        .values("sum_delivered_quantity")[:1]
    )
    total_cash_received_usd_payment_subquery = Subquery(
        Payment.objects.filter(status__in=Payment.ALLOW_CREATE_VERIFICATION, household__pk=OuterRef("pk"))
        .values("household__pk")
        .annotate(sum_delivered_quantity_usd=Sum("delivered_quantity_usd"))
        .values("sum_delivered_quantity_usd")[:1]
    )
    Household.objects.filter(id__in=id_list).annotate(
        total_cash_received_from_payment_records=Coalesce(total_cash_received_payment_record_subquery, 0),
        total_cash_received_from_payments=Coalesce(total_cash_received_payment_subquery, 0),
        total_cash_received_from_payment_records_usd=Coalesce(total_cash_received_usd_payment_record_subquery, 0),
        total_cash_received_from_payments_usd=Coalesce(total_cash_received_usd_payment_subquery, 0),
    ).update(
        total_cash_received=F("total_cash_received_from_payment_records") + F("total_cash_received_from_payments"),
        total_cash_received_usd=F("total_cash_received_from_payment_records_usd")
        + F("total_cash_received_from_payments_usd"),
    )
