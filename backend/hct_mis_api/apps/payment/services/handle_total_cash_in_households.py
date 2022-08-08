from django.db.models import Sum, Subquery, OuterRef
from django.db.models.functions import Coalesce

from hct_mis_api.apps.household.models import Household
from hct_mis_api.apps.payment.models import PaymentRecord


def handle_total_cash_in_specific_households(id_list):
    # TODO MB include payment plans
    total_cash_received_subquery = Subquery(
        PaymentRecord.objects.filter(household__pk=OuterRef("pk"))
        .values("household__pk")
        .annotate(sum_delivered_quantity=Sum("delivered_quantity"))
        .values("sum_delivered_quantity")[:1]
    )
    total_cash_received_usd_subquery = Subquery(
        PaymentRecord.objects.filter(household__pk=OuterRef("pk"))
        .values("household__pk")
        .annotate(sum_delivered_quantity_usd=Sum("delivered_quantity_usd"))
        .values("sum_delivered_quantity_usd")[:1]
    )
    Household.objects.filter(id__in=id_list).update(
        total_cash_received=Coalesce(total_cash_received_subquery, 0),
        total_cash_received_usd=Coalesce(total_cash_received_usd_subquery, 0),
    )


def handle_total_cash_in_households(only_new=False):
    base_queryset = Household.objects.all()
    if only_new:
        base_queryset = base_queryset.filter(total_cash_received_usd__isnull=True, total_cash_received__isnull=True)
    id_list = list(base_queryset[:500].values_list("id", flat=True))
    while len(id_list):
        handle_total_cash_in_specific_households(id_list)
        id_list = list(base_queryset[:500].values_list("id", flat=True))
