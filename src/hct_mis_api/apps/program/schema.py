from typing import Any

from django.db.models import Count, DecimalField, F, Q, QuerySet, Sum

import graphene

from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.decorators import cached_in_django_cache
from hct_mis_api.apps.core.utils import (
    chart_filters_decoder,
    chart_permission_decorator,
)
from hct_mis_api.apps.payment.models import DeliveryMechanism
from hct_mis_api.apps.payment.utils import get_payment_items_for_dashboard
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.utils.schema import ChartDetailedDatasetsNode


class Query(graphene.ObjectType):
    chart_programmes_by_sector = graphene.Field(
        ChartDetailedDatasetsNode,
        business_area_slug=graphene.String(required=True),
        year=graphene.Int(required=True),
        program=graphene.String(required=False),
        administrative_area=graphene.String(required=False),
    )
    chart_total_transferred_by_month = graphene.Field(
        ChartDetailedDatasetsNode,
        business_area_slug=graphene.String(required=True),
        year=graphene.Int(required=True),
        program=graphene.String(required=False),
        administrative_area=graphene.String(required=False),
    )

    @chart_permission_decorator(permissions=[Permissions.DASHBOARD_VIEW_COUNTRY])
    @cached_in_django_cache(24)
    def resolve_chart_programmes_by_sector(self, info: Any, business_area_slug: str, year: int, **kwargs: Any) -> dict:
        filters = chart_filters_decoder(kwargs)
        sector_choice_mapping = dict(Program.SECTOR_CHOICE)
        payment_items_qs: QuerySet = get_payment_items_for_dashboard(year, business_area_slug, filters, True)

        programs_ids = payment_items_qs.values_list("parent__program_cycle__program__id", flat=True)
        programs = Program.objects.filter(id__in=programs_ids).distinct()

        programmes_by_sector = (
            programs.values("sector")
            .order_by("sector")
            .annotate(total_count_without_cash_plus=Count("id", distinct=True, filter=Q(cash_plus=False)))
            .annotate(total_count_with_cash_plus=Count("id", distinct=True, filter=Q(cash_plus=True)))
        )
        labels = []
        programmes_wo_cash_plus = []
        programmes_with_cash_plus = []
        programmes_total = []
        for programme in programmes_by_sector:
            labels.append(sector_choice_mapping.get(programme.get("sector")))
            programmes_wo_cash_plus.append(programme.get("total_count_without_cash_plus") or 0)
            programmes_with_cash_plus.append(programme.get("total_count_with_cash_plus") or 0)
            programmes_total.append(programmes_wo_cash_plus[-1] + programmes_with_cash_plus[-1])

        datasets = [
            {"label": "Programmes", "data": programmes_wo_cash_plus},
            {"label": "Programmes with Cash+", "data": programmes_with_cash_plus},
            {"label": "Total Programmes", "data": programmes_total},
        ]

        return {"labels": labels, "datasets": datasets}

    @chart_permission_decorator(permissions=[Permissions.DASHBOARD_VIEW_COUNTRY])
    @cached_in_django_cache(24)
    def resolve_chart_total_transferred_by_month(
        self, info: Any, business_area_slug: str, year: int, **kwargs: Any
    ) -> dict:
        payment_items_qs: QuerySet = get_payment_items_for_dashboard(
            year, business_area_slug, chart_filters_decoder(kwargs), True
        )

        months_and_amounts = (
            payment_items_qs.annotate(
                delivery_month=F("delivery_date__month"),
                total_delivered_cash=Sum(
                    "delivered_quantity_usd",
                    filter=Q(delivery_type__transfer_type=DeliveryMechanism.TransferType.CASH.value),
                    output_field=DecimalField(),
                ),
                total_delivered_voucher=Sum(
                    "delivered_quantity_usd",
                    filter=Q(delivery_type__transfer_type=DeliveryMechanism.TransferType.VOUCHER.value),
                    output_field=DecimalField(),
                ),
            )
            .values("delivery_month", "total_delivered_cash", "total_delivered_voucher")
            .order_by("delivery_month")
        )

        months_labels = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        previous_transfers = [0] * 12
        cash_transfers = [0] * 12
        voucher_transfers = [0] * 12

        for data_dict in months_and_amounts:
            month_index = data_dict["delivery_month"] - 1
            cash_transfers[month_index] += data_dict.get("total_delivered_cash") or 0
            voucher_transfers[month_index] += data_dict.get("total_delivered_voucher") or 0

        for index in range(1, len(months_labels)):
            previous_transfers[index] = (
                previous_transfers[index - 1] + cash_transfers[index - 1] + voucher_transfers[index - 1]
            )
        datasets = [
            {"label": "Previous Transfers", "data": previous_transfers},
            {"label": "Voucher Transferred", "data": voucher_transfers},
            {"label": "Cash Transferred", "data": cash_transfers},
        ]

        return {"labels": months_labels, "datasets": datasets}
