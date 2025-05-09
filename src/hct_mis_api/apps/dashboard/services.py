import calendar
import json
from collections import defaultdict
from typing import Any, Protocol

from django.core.cache import cache
from django.db.models import Case, Count, DecimalField, F, Q, Sum, Value, When
from django.db.models.functions import Coalesce, ExtractMonth, ExtractYear

from rest_framework.utils.serializer_helpers import ReturnDict

from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.dashboard.serializers import DashboardBaseSerializer
from hct_mis_api.apps.payment.models import Payment

CACHE_TIMEOUT = 60 * 60 * 6  # 6 hours

pwdSum = Sum(
    Coalesce(F("household__female_age_group_0_5_disabled_count"), 0)
    + Coalesce(F("household__female_age_group_6_11_disabled_count"), 0)
    + Coalesce(F("household__female_age_group_12_17_disabled_count"), 0)
    + Coalesce(F("household__female_age_group_18_59_disabled_count"), 0)
    + Coalesce(F("household__female_age_group_60_disabled_count"), 0)
    + Coalesce(F("household__male_age_group_0_5_disabled_count"), 0)
    + Coalesce(F("household__male_age_group_6_11_disabled_count"), 0)
    + Coalesce(F("household__male_age_group_12_17_disabled_count"), 0)
    + Coalesce(F("household__male_age_group_18_59_disabled_count"), 0)
    + Coalesce(F("household__male_age_group_60_disabled_count"), 0),
    default=0,
)

finished_payment_plans = Count(
    "parent__id", filter=Q(parent__payment_verification_plans__status="FINISHED"), distinct=True
)

total_payment_plans = Count("parent__id", filter=Q(parent__status="FINISHED"), distinct=True)


class DashboardDataCache(Protocol):
    """
    Utility class to manage dashboard data caching using Redis.
    """

    @staticmethod
    def get_cache_key(business_area_slug: str) -> str:
        return f"dashboard_data_{business_area_slug}"

    @classmethod
    def get_data(cls, business_area_slug: str) -> dict[str, Any] | None:
        """
        Retrieve cached dashboard data for a given business area.
        """
        cache_key = cls.get_cache_key(business_area_slug)
        data = cache.get(cache_key)
        if data:
            return json.loads(data)
        return None

    @classmethod
    def store_data(cls, business_area_slug: str, data: dict[str, Any]) -> None:
        """
        Store data in Redis cache for a given business area.
        """
        cache_key = cls.get_cache_key(business_area_slug)
        cache.set(cache_key, json.dumps(data), CACHE_TIMEOUT)

    @classmethod
    def refresh_data(cls, business_area_slug: str) -> ReturnDict:
        """
        Generate and store updated data for a given business area.
        """
        list_country = []
        business_area_ = BusinessArea.objects.using("read_only")
        if business_area_slug:
            list_country = business_area_.filter(slug=business_area_slug)
        else:
            list_country = business_area_.filter(active=True)
        result = []
        for area in list_country:
            payments_aggregated = (
                Payment.objects.using("read_only")
                .select_related(
                    "business_area",
                    "household",
                    "program",
                    "household__admin1",
                    "financial_service_provider",
                    "delivery_type",
                    "parent",
                )
                .filter(
                    business_area=area,
                    parent__status__in=["ACCEPTED", "FINISHED"],
                    is_removed=False,
                    conflicted=False,
                )  # noqa
                .exclude(status__in=["Transaction Erroneous", "Not Distributed", "Force failed", "Manually Cancelled"])
                .annotate(
                    year=ExtractYear(Coalesce("delivery_date", "entitlement_date", "status_date")),
                    month=ExtractMonth(Coalesce("delivery_date", "entitlement_date", "status_date")),
                    programs=Coalesce(F("household__program__name"), Value("Unknown program")),
                    sectors=Coalesce(F("household__program__sector"), Value("Unknown sector")),
                    admin1=Coalesce(
                        F("household__admin1__name"), F("household__admin_area__name"), Value("Unknown admin area")
                    ),
                    fsp=Coalesce(F("financial_service_provider__name"), Value("Unknown fsp")),
                    delivery_types=F("delivery_type__name"),
                )
                .order_by()
                .values(
                    "currency",
                    "year",
                    "month",
                    "status",
                    "programs",
                    "sectors",
                    "admin1",
                    "fsp",
                    "delivery_types",
                )
                .annotate(
                    total_usd=Sum(
                        Case(
                            When(delivered_quantity_usd__isnull=False, then="delivered_quantity_usd"),
                            When(entitlement_quantity_usd__isnull=False, then="entitlement_quantity_usd"),
                            default=Value(0.0),
                            output_field=DecimalField(),
                        )
                    ),
                    total_quantity=Sum(
                        Case(
                            When(delivered_quantity__isnull=False, then="delivered_quantity"),
                            When(entitlement_quantity__isnull=False, then="entitlement_quantity"),
                            default=Value(0.0),
                            output_field=DecimalField(),
                        )
                    ),
                    total_payments=Count("id", distinct=True),
                    individuals=Sum(Coalesce("household__size", Value(1))),
                    households=Count("household", distinct=True),
                    children_counts=Sum("household__children_count"),
                    reconciled=Count("pk", distinct=False, filter=Q(payment_verifications__isnull=False)),
                    pwd_counts=pwdSum,
                    finished_payment_plans=finished_payment_plans,
                    total_payment_plans=total_payment_plans,
                )
            )

            summary = defaultdict(
                lambda: {
                    "total_usd": 0,
                    "total_quantity": 0,
                    "total_payments": 0,
                    "sizes": 0,
                    "children_counts": 0,
                    "individuals": 0,
                    "households": 0,
                    "pwd_counts": 0,
                    "reconciled": 0,
                    "finished_payment_plans": 0,
                    "total_payment_plans": 0,
                }
            )
            for item in list(payments_aggregated.iterator()):
                key = (
                    item["currency"],
                    item["year"],
                    item["month"],
                    item["programs"],
                    item["sectors"],
                    item["status"],
                    item["admin1"],
                    item["fsp"],
                    item["delivery_types"],
                )
                summary[key]["total_usd"] += item["total_usd"] or 0
                summary[key]["total_quantity"] += item["total_quantity"] or 0
                summary[key]["total_payments"] += item["total_payments"] or 0
                summary[key]["individuals"] += item["individuals"] or 0
                summary[key]["households"] += item["households"] or 0
                summary[key]["children_counts"] += item["children_counts"] or 0
                summary[key]["pwd_counts"] += item["pwd_counts"] or 0
                summary[key]["reconciled"] += item["reconciled"] or 0
                summary[key]["finished_payment_plans"] += item["finished_payment_plans"]
                summary[key]["total_payment_plans"] += item["total_payment_plans"]

            for (currency, year, month, program, sector, status, admin1, fsp, delivery_type), totals in summary.items():
                result.append(
                    {
                        "currency": currency,
                        "total_delivered_quantity_usd": totals["total_usd"],
                        "total_delivered_quantity": totals["total_quantity"],
                        "payments": totals["total_payments"],
                        "individuals": totals["individuals"],
                        "households": totals["households"],
                        "children_counts": totals["children_counts"],
                        "reconciled": totals["reconciled"],
                        "finished_payment_plans": totals["finished_payment_plans"],
                        "total_payment_plans": totals["total_payment_plans"],
                        "month": calendar.month_name[month],
                        "year": year,
                        "program": program,
                        "sector": sector,
                        "status": status,
                        "admin1": admin1,
                        "fsp": fsp,
                        "delivery_types": delivery_type,
                        "pwd_counts": totals["pwd_counts"],
                    }
                )
        serialized_data = DashboardBaseSerializer(result, many=True).data

        cls.store_data(business_area_slug, serialized_data)
        return serialized_data


class DashboardGlobalDataCache(DashboardDataCache):
    """
    Utility class to manage global dashboard data caching using Redis.
    """

    @classmethod
    def refresh_data(cls, business_area_slug: str = "global") -> ReturnDict:
        """
        Generate and store updated data for the global dashboard.
        """
        result = []
        payments_aggregated = (
            Payment.objects.using("read_only")
            .select_related(
                "business_area",
                "delivery_type",
                "parent",
            )
            .filter(
                parent__status__in=["ACCEPTED", "FINISHED"],
                is_removed=False,
                conflicted=False,
            )  # noqa
            .exclude(status__in=["Transaction Erroneous", "Not Distributed", "Force failed", "Manually Cancelled"])
            .annotate(
                country=F("business_area__name"),
                year=ExtractYear(Coalesce("delivery_date", "entitlement_date", "status_date")),
                sectors=Coalesce(F("household__program__sector"), Value("Unknown sector")),
                delivery_types=F("delivery_type__name"),
            )
            .order_by()
            .values(
                "country",
                "currency",
                "status",
                "year",
                "sectors",
                "delivery_types",
            )
            .annotate(
                total_usd=Sum(
                    Case(
                        When(delivered_quantity_usd__isnull=False, then="delivered_quantity_usd"),
                        When(entitlement_quantity_usd__isnull=False, then="entitlement_quantity_usd"),
                        default=Value(0.0),
                        output_field=DecimalField(),
                    )
                ),
                total_payments=Count("id", distinct=True),
                individuals=Sum(Coalesce("household__size", Value(1))),
                households=Count("household", distinct=True),
                children_counts=Sum("household__children_count"),
                reconciled=Count("pk", distinct=False, filter=Q(payment_verifications__isnull=False)),
                pwd_counts=pwdSum,
                finished_payment_plans=finished_payment_plans,
                total_payment_plans=total_payment_plans,
            )
        )

        summary = defaultdict(
            lambda: {
                "total_usd": 0,
                "total_payments": 0,
                "sizes": 0,
                "children_counts": 0,
                "individuals": 0,
                "households": 0,
                "pwd_counts": 0,
                "reconciled": 0,
                "finished_payment_plans": 0,
                "total_payment_plans": 0,
            }
        )

        for item in list(payments_aggregated.iterator()):
            key = (
                item["currency"],
                item["year"],
                item["status"],
                item["country"],
                item["sectors"],
                item["delivery_types"],
            )
            summary[key]["total_usd"] += item["total_usd"] or 0
            summary[key]["total_payments"] += item["total_payments"] or 0
            summary[key]["individuals"] += item["individuals"] or 0
            summary[key]["households"] += item["households"] or 0
            summary[key]["children_counts"] += item["children_counts"] or 0
            summary[key]["pwd_counts"] += item["pwd_counts"] or 0
            summary[key]["reconciled"] += item["reconciled"] or 0
            summary[key]["finished_payment_plans"] += item["finished_payment_plans"]
            summary[key]["total_payment_plans"] += item["total_payment_plans"]

        for (
            currency,
            year,
            status,
            country,
            sector,
            delivery_type,
        ), totals in summary.items():
            result.append(
                {
                    "currency": currency,
                    "status": status,
                    "total_delivered_quantity_usd": totals["total_usd"],
                    "payments": totals["total_payments"],
                    "individuals": totals["individuals"],
                    "households": totals["households"],
                    "children_counts": totals["children_counts"],
                    "pwd_counts": totals["pwd_counts"],
                    "reconciled": totals["reconciled"],
                    "finished_payment_plans": totals["finished_payment_plans"],
                    "total_payment_plans": totals["total_payment_plans"],
                    "year": year,
                    "country": country,
                    "sector": sector,
                    "delivery_types": delivery_type,
                }
            )

        serialized_data = DashboardBaseSerializer(result, many=True).data

        cls.store_data("global", serialized_data)
        return serialized_data
