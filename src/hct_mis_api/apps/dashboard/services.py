import calendar
import json
from collections import defaultdict
from typing import Any, Dict, List, Optional, Protocol, Set, Tuple

from django.core.cache import cache
from django.db import models
from django.db.models import Count, DecimalField, F, Q, Value
from django.db.models.functions import Coalesce, ExtractMonth, ExtractYear

from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.dashboard.serializers import DashboardBaseSerializer
from hct_mis_api.apps.household.models import Household
from hct_mis_api.apps.payment.models import Payment

CACHE_TIMEOUT = 60 * 60 * 6  # 6 hours
GLOBAL_SLUG = "global"


def get_pwd_count_expression() -> models.Expression:
    """Returns the Django ORM expression to calculate total PWD count per household."""
    fields_to_sum = [
        Coalesce(F(f"{field_name}"), 0)
        for field_name in [
            "female_age_group_0_5_disabled_count",
            "female_age_group_6_11_disabled_count",
            "female_age_group_12_17_disabled_count",
            "female_age_group_18_59_disabled_count",
            "female_age_group_60_disabled_count",
            "male_age_group_0_5_disabled_count",
            "male_age_group_6_11_disabled_count",
            "male_age_group_12_17_disabled_count",
            "male_age_group_18_59_disabled_count",
            "male_age_group_60_disabled_count",
        ]
    ]
    return sum(fields_to_sum, start=Value(0))


class DashboardCacheBase(Protocol):
    """
    Base class providing shared utilities for dashboard caching.
    Subclasses should implement the refresh_data method.
    """

    CACHE_KEY_PREFIX = "dashboard_data_"

    @classmethod
    def get_cache_key(cls, identifier: str) -> str:
        """Generates a cache key."""
        return f"{cls.CACHE_KEY_PREFIX}{identifier}"

    @classmethod
    def get_data(cls, identifier: str) -> Optional[List[Dict[str, Any]]]:
        """Retrieves and parses cached dashboard data."""
        cache_key = cls.get_cache_key(identifier)
        data = cache.get(cache_key)
        try:
            return json.loads(data) if data else None
        except json.JSONDecodeError:
            return None

    @classmethod
    def store_data(cls, identifier: str, data: List[Dict[str, Any]]) -> None:
        """Serializes and stores dashboard data in the cache."""
        cache_key = cls.get_cache_key(identifier)
        try:
            cache.set(cache_key, json.dumps(data), CACHE_TIMEOUT)
        except TypeError as e:
            raise TypeError(f"Failed to serialize data for cache storage: {e}")

    @classmethod
    def _get_base_payment_queryset(cls, business_area: Optional[BusinessArea] = None) -> models.QuerySet:
        """
        Returns a base queryset for Payment objects with common filters.
        Includes necessary select_related for subsequent annotations.
        """
        qs = (
            Payment.objects.using("read_only")
            .select_related(
                "business_area",
                "household",
                "household__admin1",
                "household__admin_area",
                "household__program",
                "program",
                "financial_service_provider",
                "delivery_type",
                "parent",
                "parent__program",
            )
            .filter(
                parent__status__in=["ACCEPTED", "FINISHED"],
                program__is_visible=True,
                parent__is_removed=False,
                is_removed=False,
                conflicted=False,
            )
            .exclude(status__in=["Transaction Erroneous", "Not Distributed", "Force failed", "Manually Cancelled"])
        )

        if business_area:
            qs = qs.filter(business_area=business_area)
        return qs

    @classmethod
    def _get_payment_data(cls, base_queryset: models.QuerySet) -> models.QuerySet:
        """
        Annotates the base payment queryset with calculated fields needed for aggregation.
        Does NOT perform grouping/summation here.
        """
        date_field = Coalesce("delivery_date", "entitlement_date", "status_date")  # Define reliable date source

        return base_queryset.annotate(
            payment_quantity_usd=Coalesce(
                F("delivered_quantity_usd"), F("entitlement_quantity_usd"), Value(0.0), output_field=DecimalField()
            ),
            payment_quantity=Coalesce(
                F("delivered_quantity"), F("entitlement_quantity"), Value(0.0), output_field=DecimalField()
            ),
            year=ExtractYear(date_field),
            month=ExtractMonth(date_field),
            business_area_name=Coalesce(F("business_area__name"), Value("Unknown Country")),
            currency_code=Coalesce(F("currency"), Value("UNK")),
            admin1_name=Coalesce(
                F("household__admin1__name"), F("household__admin_area__name"), Value("Unknown Admin1")
            ),
            program_name=Coalesce(F("household__program__name"), Value("Unknown Program")),
            sector_name=Coalesce(F("household__program__sector"), Value("Unknown Sector")),
            fsp_name=Coalesce(F("financial_service_provider__name"), Value("Unknown FSP")),
            delivery_type_name=Coalesce(F("delivery_type__name"), Value("Unknown Delivery Type")),
            payment_status=Coalesce(F("status"), Value("Unknown Status")),
            reconciled=Count("pk", filter=Q(payment_verifications__isnull=False), distinct=False),
            household_id_val=F("household_id"),
            parent_id_val=F("parent_id"),
        ).values(
            "payment_quantity_usd",
            "payment_quantity",
            "year",
            "month",
            "business_area_name",
            "currency_code",
            "admin1_name",
            "program_name",
            "sector_name",
            "fsp_name",
            "delivery_type_name",
            "payment_status",
            "reconciled",
            "household_id_val",
            "parent_id_val",
        )

    @classmethod
    def _get_household_data(cls, household_ids: Set[int]) -> Dict[int, Dict[str, Any]]:
        """
        Fetches unique household data for the given IDs.
        Returns a dictionary keyed by household_id.
        """
        if not household_ids:
            return {}

        households_qs = (
            Household.objects.using("read_only")
            .filter(id__in=household_ids)
            .select_related("admin1", "admin_area", "business_area")
            .annotate(
                pwd_count_calc=get_pwd_count_expression(),
                admin1_name_hh=Coalesce(F("admin1__name"), F("admin_area__name"), Value("Unknown Admin1")),
                country_name_hh=Coalesce(F("business_area__name"), Value("Unknown Country")),
            )
            .values(
                "id",
                "size",
                "children_count",
                "pwd_count_calc",
                "admin1_name_hh",
                "country_name_hh",
            )
        )

        household_map = {}
        for hh in households_qs:
            household_map[hh["id"]] = {
                "size": hh.get("size") or 0,
                "children_count": hh.get("children_count") or 0,
                "pwd_count": hh.get("pwd_count_calc") or 0,
                "admin1": hh.get("admin1_name_hh", "Unknown Admin1"),
                "country": hh.get("country_name_hh", "Unknown Country"),
            }
        return household_map

    @classmethod
    def _get_payment_plan_counts(
        cls, base_queryset: models.QuerySet, group_by_fields: List[str]
    ) -> Dict[str, Dict[Tuple, int]]:
        """
        Calculates total and finished distinct payment plan counts.
        """
        plans_base = base_queryset.filter(parent_id__isnull=False).values_list("parent_id", *group_by_fields).distinct()

        total_counts = defaultdict(int)
        for plan_data in plans_base:
            key = tuple(plan_data[1:])
            total_counts[key] += 1

        finished_plans_base = (
            base_queryset.filter(parent_id__isnull=False, parent__payment_verification_plans__status="FINISHED")
            .values_list("parent_id", *group_by_fields)
            .distinct()
        )

        finished_counts = defaultdict(int)
        for plan_data in finished_plans_base:
            key = tuple(plan_data[1:])
            finished_counts[key] += 1

        return {"total": dict(total_counts), "finished": dict(finished_counts)}

    def refresh_data(self, identifier: str) -> List[Dict[str, Any]]:
        """Placeholder: Subclasses must implement this."""
        raise NotImplementedError


class DashboardDataCache(DashboardCacheBase):
    """Handles caching for country-specific dashboards."""

    @classmethod
    def refresh_data(cls, business_area_slug: str) -> List[Dict[str, Any]]:
        """Generates and caches data for a specific country."""
        try:
            business_area = BusinessArea.objects.using("read_only").get(slug=business_area_slug)
        except BusinessArea.DoesNotExist:
            cls.store_data(business_area_slug, [])
            return []

        base_payments_qs = cls._get_base_payment_queryset(business_area=business_area)

        household_ids = set(base_payments_qs.values_list("household_id", flat=True).distinct())
        if not household_ids:
            cls.store_data(business_area_slug, [])
            return []

        household_map = cls._get_household_data(household_ids)

        plan_group_fields = ["currency", "household__program__name", "household__program__sector"]
        plan_counts = cls._get_payment_plan_counts(base_payments_qs, plan_group_fields)

        payment_data_iter = cls._get_payment_data(base_payments_qs).iterator()

        summary = defaultdict(
            lambda: {
                "total_usd": 0.0,
                "total_quantity": 0.0,
                "total_payments": 0,
                "individuals": 0,
                "children_counts": 0,
                "pwd_counts": 0,
                "reconciled_count": 0,
                "finished_payment_plans": 0,
                "total_payment_plans": 0,
                "_seen_households": set(),
            }
        )

        for payment in payment_data_iter:
            year = payment.get("year")
            month = payment.get("month")
            if year is None or month is None:
                continue

            key = (
                year,
                month,
                payment.get("admin1_name", "Unknown Admin1"),
                payment.get("program_name", "Unknown Program"),
                payment.get("sector_name", "Unknown Sector"),
                payment.get("fsp_name", "Unknown FSP"),
                payment.get("delivery_type_name", "Unknown Delivery Type"),
                payment.get("payment_status", "Unknown Status"),
                payment.get("currency_code", "UNK"),
            )

            plan_key = tuple(payment.get(field, None) for field in plan_group_fields)
            summary[key]["finished_payment_plans"] = plan_counts["finished"].get(plan_key, 0)
            summary[key]["total_payment_plans"] = plan_counts["total"].get(plan_key, 0)

            summary[key]["total_usd"] += float(payment.get("payment_quantity_usd") or 0)
            summary[key]["total_quantity"] += float(payment.get("payment_quantity") or 0)
            summary[key]["total_payments"] += 1
            summary[key]["reconciled_count"] += payment.get("reconciled", 0)

            household_id = payment.get("household_id_val")
            if household_id and household_id not in summary[key]["_seen_households"]:
                h_data = household_map.get(household_id, {})
                summary[key]["individuals"] += h_data.get("size", 0)
                summary[key]["children_counts"] += h_data.get("children_count", 0)
                summary[key]["pwd_counts"] += h_data.get("pwd_count", 0)
                summary[key]["_seen_households"].add(household_id)
        result_list = []
        for (year, month, admin1, program, sector, fsp, delivery_type, status, currency), totals in summary.items():
            month_name = "Unknown"
            if month and 1 <= month <= 12:
                month_name = calendar.month_name[month]

            result_list.append(
                {
                    "year": year,
                    "month": month_name,
                    "admin1": admin1,
                    "program": program,
                    "sector": sector,
                    "fsp": fsp,
                    "delivery_types": delivery_type,
                    "status": status,
                    "currency": currency,
                    "total_delivered_quantity_usd": totals["total_usd"],
                    "total_delivered_quantity": totals["total_quantity"],
                    "payments": totals["total_payments"],
                    "households": len(totals["_seen_households"]),
                    "individuals": totals["individuals"],
                    "children_counts": totals["children_counts"],
                    "pwd_counts": totals["pwd_counts"],
                    "reconciled": totals["reconciled_count"],
                    "finished_payment_plans": totals["finished_payment_plans"],
                    "total_payment_plans": totals["total_payment_plans"],
                }
            )

        try:
            serialized_data = DashboardBaseSerializer(result_list, many=True).data
            cls.store_data(business_area_slug, serialized_data)
            return serialized_data
        except Exception as e:
            cls.store_data(business_area_slug, result_list)
            return result_list


class DashboardGlobalDataCache(DashboardCacheBase):
    """Handles caching for the global dashboard."""

    @classmethod
    def refresh_data(cls, identifier: str = GLOBAL_SLUG) -> List[Dict[str, Any]]:
        """Generates and caches data for the global view."""
        if identifier != GLOBAL_SLUG:
            identifier = GLOBAL_SLUG

        base_payments_qs = cls._get_base_payment_queryset()

        household_ids = set(base_payments_qs.values_list("household_id", flat=True).distinct())
        if not household_ids:
            cls.store_data(identifier, [])
            return []

        household_map = cls._get_household_data(household_ids)

        plan_group_fields = ["household__program__sector"]
        plan_counts = cls._get_payment_plan_counts(base_payments_qs, plan_group_fields)

        payment_data_iter = cls._get_payment_data(base_payments_qs).iterator()

        summary = defaultdict(
            lambda: {
                "total_usd": 0.0,
                "total_payments": 0,
                "individuals": 0,
                "children_counts": 0,
                "pwd_counts": 0,
                "reconciled_count": 0,
                "finished_payment_plans": 0,
                "total_payment_plans": 0,
                "_seen_households": set(),
            }
        )

        for payment in payment_data_iter:
            year = payment.get("year")
            if year is None:
                continue

            key = (
                year,
                payment.get("business_area_name", "Unknown Country"),
                payment.get("sector_name", "Unknown Sector"),
                payment.get("delivery_type_name", "Unknown Delivery Type"),
                payment.get("payment_status", "Unknown Status"),
            )

            plan_key = tuple(payment.get(field, None) for field in plan_group_fields)
            summary[key]["finished_payment_plans"] = plan_counts["finished"].get(plan_key, 0)
            summary[key]["total_payment_plans"] = plan_counts["total"].get(plan_key, 0)
            summary[key]["total_usd"] += float(payment.get("payment_quantity_usd") or 0)
            summary[key]["total_payments"] += 1
            summary[key]["reconciled_count"] += payment.get("reconciled", 0)
            household_id = payment.get("household_id_val")
            if household_id and household_id not in summary[key]["_seen_households"]:
                h_data = household_map.get(household_id, {})
                summary[key]["individuals"] += h_data.get("size", 0)
                summary[key]["children_counts"] += h_data.get("children_count", 0)
                summary[key]["pwd_counts"] += h_data.get("pwd_count", 0)
                summary[key]["_seen_households"].add(household_id)
        result_list = []
        for (year, country, sector, delivery_type, status), totals in summary.items():
            result_list.append(
                {
                    "year": year,
                    "country": country,
                    "sector": sector,
                    "delivery_types": delivery_type,
                    "status": status,
                    "total_delivered_quantity_usd": totals["total_usd"],
                    "payments": totals["total_payments"],
                    "households": len(totals["_seen_households"]),
                    "individuals": totals["individuals"],
                    "children_counts": totals["children_counts"],
                    "pwd_counts": totals["pwd_counts"],
                    "reconciled": totals["reconciled_count"],
                    "finished_payment_plans": totals["finished_payment_plans"],
                    "total_payment_plans": totals["total_payment_plans"],
                }
            )
        try:
            serialized_data = DashboardBaseSerializer(result_list, many=True).data
            cls.store_data(identifier, serialized_data)
            return serialized_data
        except Exception as e:
            cls.store_data(identifier, result_list)
            return result_list
