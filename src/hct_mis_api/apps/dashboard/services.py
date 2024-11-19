import calendar
import json
from collections import defaultdict
from typing import Any, Dict, Optional

from django.core.cache import cache
from django.db.models import Count, DecimalField, F, Sum, Value 
from django.db.models.functions import Coalesce, ExtractMonth, ExtractYear

from rest_framework.utils.serializer_helpers import ReturnDict

from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.dashboard.serializers import DashboardHouseholdSerializer
from hct_mis_api.apps.payment.models import Payment, PaymentRecord

CACHE_TIMEOUT = 60 * 60 * 24  # 24 hours

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


class DashboardDataCache:
    """
    Utility class to manage dashboard data caching using Redis.
    """

    @staticmethod
    def get_cache_key(business_area_slug: str) -> str:
        return f"dashboard_data_{business_area_slug}"

    @classmethod
    def get_data(cls, business_area_slug: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve cached dashboard data for a given business area.
        """
        cache_key = cls.get_cache_key(business_area_slug)
        data = cache.get(cache_key)
        if data:
            return json.loads(data)
        return None

    @classmethod
    def store_data(cls, business_area_slug: str, data: Dict[str, Any]) -> None:
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
                )
                .filter(business_area=area, household__is_removed=False)
                .annotate(
                    year=ExtractYear(Coalesce("delivery_date", "entitlement_date", "status_date")),
                    month=ExtractMonth(Coalesce("delivery_date", "entitlement_date", "status_date")),
                    programs=Coalesce(F("household__program__name"), Value("Unknown program")),
                    sectors=Coalesce(F("household__program__sector"), Value("Unknown sector")),
                    admin1=Coalesce(F("household__admin1__name"), Value("Unknown admin1")),
                    fsp=Coalesce(F("financial_service_provider__name"), Value("Unknown fsp")),
                    delivery_types=Coalesce(F("delivery_type__name"), F("delivery_type_choice")),
                )
                .distinct()
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
                    total_usd=Sum(Coalesce("delivered_quantity_usd", "entitlement_quantity_usd", Value(0.0)), output_field=DecimalField()),
                    total_quantity=Sum(Coalesce("delivered_quantity", "entitlement_quantity", Value(0.0)), output_field=DecimalField()),
                    total_payments=Count("id", distinct=True),
                    individuals=Sum("household__size"),
                    households=Count("household", distinct=True),
                    children_counts=Sum("household__children_count"),
                    pwd_counts=pwdSum,
                )
            )

            payment_records_aggregated = (
                PaymentRecord.objects.using("read_only")
                .select_related(
                    "business_area", "household", "program", "household__admin1", "service_provider", "delivery_type"
                )
                .filter(business_area=area, household__is_removed=False)
                .annotate(
                    year=ExtractYear(Coalesce("delivery_date", "status_date")),
                    month=ExtractMonth(Coalesce("delivery_date", "status_date")),
                    programs=Coalesce(F("household__program__name"), Value("Unknown program")),
                    sectors=Coalesce(F("household__program__sector"), Value("Unknown sector")),
                    admin1=Coalesce(F("household__admin1__name"), Value("Unknown admin1")),
                    fsp=Coalesce(F("service_provider__short_name"), Value("Unknown fsp")),
                    delivery_types=Coalesce(F("delivery_type__name"), F("delivery_type_choice")),
                )
                .distinct()
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
                    total_usd=Sum(Coalesce("delivered_quantity_usd", "entitlement_quantity_usd", Value(0.0)), output_field=DecimalField()),
                    total_quantity=Sum(Coalesce("delivered_quantity", "entitlement_quantity", Value(0.0)), output_field=DecimalField()),
                    total_payments=Count("id", distinct=True),
                    individuals=Sum("household__size"),
                    households=Count("household", distinct=True),
                    children_counts=Sum("household__children_count"),
                    pwd_counts=pwdSum,
                )
            )

            combined_list = list(payments_aggregated) + list(payment_records_aggregated)

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
                }
            )
            for item in combined_list:
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
        serialized_data = DashboardHouseholdSerializer(result, many=True).data

        cls.store_data(business_area_slug, serialized_data)
        return serialized_data
