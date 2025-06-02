import calendar
import json
from collections import defaultdict
from typing import (
    Any,
    Dict,
    List,
    Optional,
    Protocol,
    Set,
    Tuple,
    TypedDict,
    Union,
    cast,
)
from uuid import UUID

from django.core.cache import cache
from django.db import models
from django.db.models import Count, DecimalField, F, Q, Value
from django.db.models.functions import Coalesce, ExtractMonth, ExtractYear

from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.dashboard.serializers import DashboardBaseSerializer
from hct_mis_api.apps.household.models import Household
from hct_mis_api.apps.payment.models import Payment, PaymentPlan

CACHE_TIMEOUT = 60 * 60 * 6
GLOBAL_SLUG = "global"
DEFAULT_ITERATOR_CHUNK_SIZE = 2000
HOUSEHOLD_BATCH_SIZE = 2000


class CountrySummaryDict(TypedDict):
    total_usd: float
    total_quantity: float
    total_payments: int
    individuals: int
    children_counts: int
    pwd_counts: int
    reconciled_count: int
    finished_payment_plans: int
    total_payment_plans: int
    planned_sum_for_group: float
    _seen_households: Set[UUID]


class GlobalSummaryDict(TypedDict):
    total_usd: float
    total_payments: int
    individuals: int
    children_counts: int
    pwd_counts: int
    reconciled_count: int
    finished_payment_plans: int
    total_payment_plans: int
    planned_sum_for_group: float
    _seen_households: Set[UUID]


def get_pwd_count_expression() -> models.Expression:
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
    CACHE_KEY_PREFIX = "dashboard_data_"

    @classmethod
    def get_cache_key(cls, identifier: str) -> str:
        return f"{cls.CACHE_KEY_PREFIX}{identifier}"

    @classmethod
    def get_data(cls, identifier: str) -> Optional[List[Dict[str, Any]]]:
        cache_key = cls.get_cache_key(identifier)
        data = cache.get(cache_key)
        return json.loads(data) if data else None

    @classmethod
    def store_data(cls, identifier: str, data: List[Dict[str, Any]]) -> None:
        cache_key = cls.get_cache_key(identifier)
        cache.set(cache_key, json.dumps(data), CACHE_TIMEOUT)

    @classmethod
    def _get_base_payment_queryset(cls, business_area: Optional[BusinessArea] = None) -> models.QuerySet:
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
                parent__status__in=[
                    PaymentPlan.Status.IN_APPROVAL,
                    PaymentPlan.Status.IN_AUTHORIZATION,
                    PaymentPlan.Status.IN_REVIEW,
                    PaymentPlan.Status.ACCEPTED,
                    PaymentPlan.Status.FINISHED,
                ],
                program__is_visible=True,
                parent__is_removed=False,
                is_removed=False,
                conflicted=False,
                excluded=False,
            )
            .exclude(status__in=["Transaction Erroneous", "Not Distributed", "Force failed", "Manually Cancelled"])
        )

        if business_area:
            qs = qs.filter(business_area=business_area)
        return qs

    @classmethod
    def _get_payment_data(cls, base_queryset: models.QuerySet) -> models.QuerySet:
        date_field = Coalesce("delivery_date", "entitlement_date", "status_date")
        PLANNED_STATUSES = [
            PaymentPlan.Status.IN_APPROVAL,
            PaymentPlan.Status.IN_AUTHORIZATION,
            PaymentPlan.Status.IN_REVIEW,
        ]

        return base_queryset.annotate(
            payment_quantity_usd=Coalesce(
                F("delivered_quantity_usd"), F("entitlement_quantity_usd"), Value(0.0), output_field=DecimalField()
            ),
            payment_quantity=Coalesce(
                F("delivered_quantity"), F("entitlement_quantity"), Value(0.0), output_field=DecimalField()
            ),
            total_planned_usd_for_this_payment=models.Case(
                models.When(
                    parent__status__in=PLANNED_STATUSES, then=Coalesce(F("entitlement_quantity_usd"), Value(0.0))
                ),
                default=Value(0.0),
                output_field=DecimalField(),
            ),
            year=ExtractYear(date_field),
            month=ExtractMonth(date_field),
            business_area_name=Coalesce(F("business_area__name"), Value("Unknown Country")),
            region_name=Coalesce(F("business_area__region_name"), Value("Unknown Region")),
            currency_code=Coalesce(F("currency"), Value("UNK")),
            admin1_name=Coalesce(
                F("household__admin1__name"), F("household__admin_area__name"), Value("Unknown Admin1")
            ),
            program_name=Coalesce(F("program__name"), F("household__program__name"), Value("Unknown Program")),
            sector_name=Coalesce(F("program__sector"), F("household__program__sector"), Value("Unknown Sector")),
            fsp_name=Coalesce(F("financial_service_provider__name"), Value("Unknown FSP")),
            delivery_type_name=Coalesce(F("delivery_type__name"), Value("Unknown Delivery Type")),
            payment_status=Coalesce(F("status"), Value("Unknown Status")),
            reconciled=Count("pk", filter=Q(payment_verifications__isnull=False), distinct=True),
            household_id_val=F("household_id"),
            parent_id_val=F("parent_id"),
        ).values(
            "payment_quantity_usd",
            "payment_quantity",
            "year",
            "month",
            "business_area_name",
            "region_name",
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
            "total_planned_usd_for_this_payment",
        )

    @classmethod
    def _get_household_data(cls, household_ids: Set[UUID]) -> Dict[UUID, Dict[str, Any]]:
        if not household_ids:
            return {}

        household_map: Dict[UUID, Dict[str, Any]] = {}
        household_id_list = list(household_ids)

        for i in range(0, len(household_id_list), HOUSEHOLD_BATCH_SIZE):
            batch_ids = household_id_list[i : i + HOUSEHOLD_BATCH_SIZE]
            if not batch_ids:
                continue

            households_qs = (
                Household.objects.using("read_only")
                .filter(id__in=batch_ids)
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

            for hh in households_qs:
                size_value = hh.get("size")
                household_map[hh["id"]] = {
                    "size": 1 if size_value is None else size_value,
                    "children_count": hh.get("children_count") or 0,
                    "pwd_count": hh.get("pwd_count_calc") or 0,
                    "admin1": hh.get("admin1_name_hh", "Unknown Admin1"),
                    "country": hh.get("country_name_hh", "Unknown Country"),
                }
        return household_map

    @classmethod
    def _get_payment_plan_counts(
        cls, base_queryset: models.QuerySet, group_by_annotated_names: List[str]
    ) -> Dict[str, Dict[Tuple, int]]:
        date_field: Union[F, Coalesce] = Coalesce("delivery_date", "entitlement_date", "status_date")
        potential_annotations = {
            "year": ExtractYear(date_field),
            "month": ExtractMonth(date_field),
            "business_area_name": Coalesce(F("business_area__name"), Value("Unknown Country")),
            "region_name": Coalesce(F("business_area__region_name"), Value("Unknown Region")),
            "currency_code": Coalesce(F("currency"), Value("UNK")),
            "admin1_name": Coalesce(
                F("household__admin1__name"), F("household__admin_area__name"), Value("Unknown Admin1")
            ),
            "program_name": Coalesce(F("program__name"), F("household__program__name"), Value("Unknown Program")),
            "sector_name": Coalesce(F("program__sector"), F("household__program__sector"), Value("Unknown Sector")),
            "fsp_name": Coalesce(F("financial_service_provider__name"), Value("Unknown FSP")),
            "delivery_type_name": Coalesce(F("delivery_type__name"), Value("Unknown Delivery Type")),
            "payment_status": Coalesce(F("status"), Value("Unknown Status")),
        }

        relevant_annotations = {
            name: expr for name, expr in potential_annotations.items() if name in group_by_annotated_names
        }
        annotated_plans_qs = base_queryset.filter(parent_id__isnull=False).annotate(**relevant_annotations)
        plans_base = annotated_plans_qs.values_list("parent_id", *group_by_annotated_names).distinct()

        total_counts = defaultdict(int)
        for plan_data in plans_base:
            key = tuple(plan_data[1:])
            total_counts[key] += 1

        finished_plans_base = (
            annotated_plans_qs.filter(parent__payment_verification_plans__status="FINISHED")
            .values_list("parent_id", *group_by_annotated_names)
            .distinct()
        )

        finished_counts = defaultdict(int)
        for plan_data in finished_plans_base:
            key = tuple(plan_data[1:])
            finished_counts[key] += 1

        return {"total": dict(total_counts), "finished": dict(finished_counts)}

    @classmethod
    def refresh_data(cls, identifier: str, years_to_refresh: Optional[List[int]] = None) -> List[Dict[str, Any]]:
        raise NotImplementedError


class DashboardDataCache(DashboardCacheBase):
    @classmethod
    def refresh_data(
        cls, business_area_slug: str, years_to_refresh: Optional[List[int]] = None
    ) -> List[Dict[str, Any]]:
        existing_data_for_other_years: List[Dict[str, Any]] = []
        is_partial_refresh_attempt = bool(years_to_refresh)

        if is_partial_refresh_attempt and years_to_refresh:
            cache_key = cls.get_cache_key(business_area_slug)
            cached_data_str = cache.get(cache_key)
            if cached_data_str:
                all_cached_data = json.loads(cached_data_str)
                existing_data_for_other_years = [
                    item for item in all_cached_data if item.get("year") not in years_to_refresh
                ]
            else:
                is_partial_refresh_attempt = False
                years_to_refresh = None

        try:
            business_area = BusinessArea.objects.using("read_only").get(slug=business_area_slug)
        except BusinessArea.DoesNotExist:
            cls.store_data(business_area_slug, [])
            return []

        base_payments_qs = cls._get_base_payment_queryset(business_area=business_area)

        if is_partial_refresh_attempt and years_to_refresh:
            date_field_expr: Union[F, Coalesce] = Coalesce("delivery_date", "entitlement_date", "status_date")
            if base_payments_qs.exists():
                base_payments_qs = base_payments_qs.annotate(_temp_refresh_year=ExtractYear(date_field_expr)).filter(
                    _temp_refresh_year__in=years_to_refresh
                )

        household_ids: Set[UUID] = set(
            hh_id for hh_id in base_payments_qs.values_list("household_id", flat=True).distinct() if hh_id is not None
        )

        if not household_ids:
            final_result_list = existing_data_for_other_years if is_partial_refresh_attempt else []
            serialized_data = cast(List[Dict[str, Any]], DashboardBaseSerializer(final_result_list, many=True).data)
            cls.store_data(business_area_slug, serialized_data)
            return serialized_data

        household_map = cls._get_household_data(household_ids)

        if not base_payments_qs.exists() and is_partial_refresh_attempt:
            final_result_list = existing_data_for_other_years
            serialized_data = cast(List[Dict[str, Any]], DashboardBaseSerializer(final_result_list, many=True).data)
            cls.store_data(business_area_slug, serialized_data)
            return serialized_data

        plan_group_fields = [
            "year",
            "month",
            "admin1_name",
            "program_name",
            "sector_name",
            "fsp_name",
            "delivery_type_name",
            "payment_status",
            "currency_code",
        ]
        plan_counts = cls._get_payment_plan_counts(base_payments_qs, plan_group_fields)

        payment_data_iter = cls._get_payment_data(base_payments_qs.all()).iterator(
            chunk_size=DEFAULT_ITERATOR_CHUNK_SIZE
        )

        summary: defaultdict[tuple, CountrySummaryDict] = defaultdict(
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
                "planned_sum_for_group": 0.0,
                "_seen_households": set(),
            }
        )

        for payment in payment_data_iter:
            key = (
                payment.get("year"),
                payment.get("month"),
                payment.get("admin1_name", "Unknown Admin1"),
                payment.get("program_name", "Unknown Program"),
                payment.get("sector_name", "Unknown Sector"),
                payment.get("fsp_name", "Unknown FSP"),
                payment.get("delivery_type_name", "Unknown Delivery Type"),
                payment.get("payment_status", "Unknown Status"),
                payment.get("currency_code", "UNK"),
            )

            current_summary = summary[key]

            plan_key_values = [
                payment.get("year"),
                payment.get("month"),
                payment.get("admin1_name", "Unknown Admin1"),
                payment.get("program_name", "Unknown Program"),
                payment.get("sector_name", "Unknown Sector"),
                payment.get("fsp_name", "Unknown FSP"),
                payment.get("delivery_type_name", "Unknown Delivery Type"),
                payment.get("payment_status", "Unknown Status"),
                payment.get("currency_code", "UNK"),
            ]
            plan_key = tuple(plan_key_values)

            if current_summary["total_payments"] == 0:
                current_summary["finished_payment_plans"] = plan_counts["finished"].get(plan_key, 0)
                current_summary["total_payment_plans"] = plan_counts["total"].get(plan_key, 0)

            current_summary["total_usd"] += float(payment.get("payment_quantity_usd") or 0.0)
            current_summary["total_quantity"] += float(payment.get("payment_quantity") or 0.0)
            current_summary["total_payments"] += 1
            current_summary["reconciled_count"] += int(payment.get("reconciled", 0))
            current_summary["planned_sum_for_group"] += float(payment.get("total_planned_usd_for_this_payment") or 0.0)

            household_id = payment.get("household_id_val")
            if (
                household_id
                and isinstance(household_id, UUID)
                and household_id not in current_summary["_seen_households"]
            ):
                h_data = household_map.get(household_id, {})
                current_summary["individuals"] += int(h_data.get("size", 0))
                current_summary["children_counts"] += int(h_data.get("children_count", 0))
                current_summary["pwd_counts"] += int(h_data.get("pwd_count", 0))
                current_summary["_seen_households"].add(household_id)

        newly_processed_result_list = []
        for (year, month, admin1, program, sector, fsp, delivery_type, status, currency), totals in summary.items():
            month_name = "Unknown"
            if month and 1 <= month <= 12:
                month_name = calendar.month_name[month]

            newly_processed_result_list.append(
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
                    "total_planned_usd": totals["planned_sum_for_group"],
                }
            )

        final_result_list = newly_processed_result_list
        if is_partial_refresh_attempt:
            final_result_list.extend(existing_data_for_other_years)

        serialized_data = cast(List[Dict[str, Any]], DashboardBaseSerializer(final_result_list, many=True).data)
        cls.store_data(business_area_slug, serialized_data)
        return serialized_data


class DashboardGlobalDataCache(DashboardCacheBase):
    @classmethod
    def refresh_data(
        cls, identifier: str = GLOBAL_SLUG, years_to_refresh: Optional[List[int]] = None
    ) -> List[Dict[str, Any]]:
        existing_data_for_other_years: List[Dict[str, Any]] = []
        is_partial_refresh_attempt = bool(years_to_refresh)

        if is_partial_refresh_attempt and years_to_refresh:
            cache_key = cls.get_cache_key(identifier)
            cached_data_str = cache.get(cache_key)
            if cached_data_str:
                all_cached_data = json.loads(cached_data_str)
                existing_data_for_other_years = [
                    item for item in all_cached_data if item.get("year") not in years_to_refresh
                ]
            else:
                is_partial_refresh_attempt = False
                years_to_refresh = None

        base_payments_qs = cls._get_base_payment_queryset()

        if is_partial_refresh_attempt and years_to_refresh:
            date_field_expr: Union[F, Coalesce] = Coalesce("delivery_date", "entitlement_date", "status_date")
            if base_payments_qs.exists():
                base_payments_qs = base_payments_qs.annotate(_temp_refresh_year=ExtractYear(date_field_expr)).filter(
                    _temp_refresh_year__in=years_to_refresh
                )

        household_ids: Set[UUID] = set(
            hh_id for hh_id in base_payments_qs.values_list("household_id", flat=True).distinct() if hh_id is not None
        )

        if not household_ids:
            final_result_list = existing_data_for_other_years if is_partial_refresh_attempt else []
            serialized_data = cast(List[Dict[str, Any]], DashboardBaseSerializer(final_result_list, many=True).data)
            cls.store_data(identifier, serialized_data)
            return serialized_data

        household_map = cls._get_household_data(household_ids)

        plan_group_fields = [
            "year",
            "business_area_name",
            "region_name",
            "sector_name",
            "delivery_type_name",
            "payment_status",
        ]
        plan_counts = cls._get_payment_plan_counts(base_payments_qs, plan_group_fields)

        # Clone the queryset before passing to _get_payment_data to ensure it's fresh
        payment_data_iter = cls._get_payment_data(base_payments_qs.all()).iterator(
            chunk_size=DEFAULT_ITERATOR_CHUNK_SIZE
        )

        summary: defaultdict[tuple, GlobalSummaryDict] = defaultdict(
            lambda: {
                "total_usd": 0.0,
                "total_payments": 0,
                "individuals": 0,
                "children_counts": 0,
                "pwd_counts": 0,
                "reconciled_count": 0,
                "finished_payment_plans": 0,
                "total_payment_plans": 0,
                "planned_sum_for_group": 0.0,
                "_seen_households": set(),
            }
        )

        for payment in payment_data_iter:
            key = (
                payment.get("year"),
                payment.get("business_area_name", "Unknown Country"),
                payment.get("region_name", "Unknown Region"),
                payment.get("sector_name", "Unknown Sector"),
                payment.get("delivery_type_name", "Unknown Delivery Type"),
                payment.get("payment_status", "Unknown Status"),
            )
            current_summary = summary[key]

            plan_key_values = [
                payment.get("year"),
                payment.get("business_area_name", "Unknown Country"),
                payment.get("region_name", "Unknown Region"),
                payment.get("sector_name", "Unknown Sector"),
                payment.get("delivery_type_name", "Unknown Delivery Type"),
                payment.get("payment_status", "Unknown Status"),
            ]
            plan_key = tuple(plan_key_values)

            if current_summary["total_payments"] == 0:
                current_summary["finished_payment_plans"] = plan_counts["finished"].get(plan_key, 0)
                current_summary["total_payment_plans"] = plan_counts["total"].get(plan_key, 0)

            current_summary["total_usd"] += float(payment.get("payment_quantity_usd") or 0.0)
            current_summary["total_payments"] += 1
            current_summary["reconciled_count"] += int(payment.get("reconciled", 0))
            current_summary["planned_sum_for_group"] += float(payment.get("total_planned_usd_for_this_payment") or 0.0)

            household_id = payment.get("household_id_val")
            if (
                household_id
                and isinstance(household_id, UUID)
                and household_id not in current_summary["_seen_households"]
            ):
                h_data = household_map.get(household_id, {})
                current_summary["individuals"] += int(h_data.get("size", 0))
                current_summary["children_counts"] += int(h_data.get("children_count", 0))
                current_summary["pwd_counts"] += int(h_data.get("pwd_count", 0))
                current_summary["_seen_households"].add(household_id)

        newly_processed_result_list = []
        for (year, country, region, sector, delivery_type, status), totals in summary.items():
            newly_processed_result_list.append(
                {
                    "year": year,
                    "country": country,
                    "region": region,
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
                    "total_planned_usd": totals["planned_sum_for_group"],
                }
            )

        final_result_list = newly_processed_result_list
        if is_partial_refresh_attempt:
            final_result_list.extend(existing_data_for_other_years)

        serialized_data = cast(List[Dict[str, Any]], DashboardBaseSerializer(final_result_list, many=True).data)
        cls.store_data(identifier, serialized_data)
        return serialized_data
