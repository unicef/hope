from datetime import timezone as dt_timezone
from decimal import Decimal
import json
from typing import Any, Dict, Optional, Type
from unittest.mock import patch

from django.core.cache import cache
from django.utils import timezone
import pytest

from extras.test_utils.factories import (
    AreaFactory,
    AreaTypeFactory,
    BusinessAreaFactory,
    DeliveryMechanismFactory,
    FinancialServiceProviderFactory,
    HouseholdFactory,
    PaymentFactory,
    ProgramFactory,
)
from hope.apps.dashboard.serializers import DashboardBaseSerializer
from hope.apps.dashboard.services import (
    GLOBAL_SLUG,
    DashboardCacheBase,
    DashboardDataCache,
    DashboardGlobalDataCache,
)
from hope.models import BusinessArea, Payment, PaymentPlan


@pytest.fixture
def use_default_db_for_dashboard():
    with (
        patch("hope.apps.dashboard.services.settings.DASHBOARD_DB", "default"),
        patch("hope.apps.dashboard.celery_tasks.settings.DASHBOARD_DB", "default"),
    ):
        yield


pytestmark = pytest.mark.usefixtures("use_default_db_for_dashboard")

CACHE_CONFIG = [
    ("DashboardDataCache", DashboardDataCache, "test-area"),
    ("DashboardGlobalDataCache", DashboardGlobalDataCache, "global"),
]
CURRENT_YEAR = timezone.now().year
TEST_COUNTRY_SLUG = "afghanistan"
TEST_DATE = timezone.datetime(CURRENT_YEAR, 7, 15, tzinfo=dt_timezone.utc)


# ============================================================================
# Local Fixtures
# ============================================================================


@pytest.fixture
def afghanistan(db):
    return BusinessAreaFactory(
        code="0060",
        name="Afghanistan",
        long_name="THE ISLAMIC REPUBLIC OF AFGHANISTAN",
        region_code="64",
        region_name="SAR",
        slug="afghanistan",
        has_data_sharing_agreement=True,
        kobo_token="XXX",
        active=True,
    )


@pytest.fixture
def area_kabul(db):
    area_type = AreaTypeFactory(name="Province", area_level=1)
    return AreaFactory(name="Kabul", area_type=area_type)


@pytest.fixture
def populate_dashboard_cache(area_kabul):
    def _populate(ba, household_extra_args=None):
        program = ProgramFactory(business_area=ba)
        household = HouseholdFactory(
            business_area=ba,
            program=program,
            size=5,
            children_count=2,
            female_age_group_0_5_disabled_count=1,
            female_age_group_6_11_disabled_count=1,
            male_age_group_60_disabled_count=1,
            admin1=area_kabul,
            **(household_extra_args or {}),
        )
        payment_statuses = [
            Payment.STATUS_SUCCESS,
            Payment.STATUS_DISTRIBUTION_SUCCESS,
            Payment.STATUS_DISTRIBUTION_PARTIAL,
            Payment.STATUS_PENDING,
            Payment.STATUS_SUCCESS,
        ]
        for status in payment_statuses:
            PaymentFactory(
                household=household,
                program=program,
                business_area=ba,
                parent__status=PaymentPlan.Status.ACCEPTED,
                status=status,
            )
        return household

    return _populate


@pytest.fixture
def fsp_common(db):
    return FinancialServiceProviderFactory()


@pytest.fixture
def delivery_mechanism_common(db):
    return DeliveryMechanismFactory()


# ============================================================================
# Cache Key Tests
# ============================================================================


@pytest.mark.parametrize(("cache_name", "cache_class", "slug"), CACHE_CONFIG)
@pytest.mark.django_db
def test_get_cache_key(cache_name: str, cache_class: Any, slug: str) -> None:
    expected_key: str = f"dashboard_data_{slug}"
    assert cache_class.get_cache_key(slug) == expected_key


@pytest.mark.parametrize(("cache_name", "cache_class", "slug"), CACHE_CONFIG)
@pytest.mark.django_db
def test_get_data_cache_hit(cache_name: str, cache_class: Any, slug: str) -> None:
    cache.set(
        f"dashboard_data_{slug}",
        json.dumps({"test": f"{cache_name}_data"}),
        60 * 60 * 24,
    )
    data: Optional[Dict[str, Any]] = cache_class.get_data(slug)
    assert data == {"test": f"{cache_name}_data"}


@pytest.mark.parametrize(("cache_name", "cache_class", "slug"), CACHE_CONFIG)
@pytest.mark.django_db
def test_get_data_cache_miss(cache_name: str, cache_class: Any, slug: str) -> None:
    cache.delete(f"dashboard_data_{slug}")
    data: Optional[Dict[str, Any]] = cache_class.get_data(slug)
    assert data is None


@pytest.mark.parametrize(("cache_name", "cache_class", "slug"), CACHE_CONFIG)
@pytest.mark.django_db
def test_store_data(cache_name: str, cache_class: Any, slug: str) -> None:
    data: Dict[str, Any] = {"test": f"{cache_name}_data"}
    cache_class.store_data(slug, data)
    cached_data = cache.get(f"dashboard_data_{slug}")
    assert cached_data is not None
    assert json.loads(cached_data) == data


# ============================================================================
# Refresh Data Tests
# ============================================================================


@pytest.mark.parametrize(
    ("cache_name", "cache_class", "slug", "expected_optional_fields"),
    [
        (
            "DashboardDataCache",
            DashboardDataCache,
            "afghanistan",
            {"month", "admin1", "currency", "total_delivered_quantity"},
        ),
        (
            "DashboardGlobalDataCache",
            DashboardGlobalDataCache,
            "global",
            {"country"},
        ),
    ],
)
@pytest.mark.django_db
def test_refresh_data(
    cache_name: str,
    cache_class: Any,
    slug: str,
    expected_optional_fields: set,
    afghanistan: BusinessArea,
    populate_dashboard_cache,
) -> None:
    cache_key = cache_class.get_cache_key(slug)
    cache.delete(cache_key)

    populate_dashboard_cache(afghanistan)

    refreshed_data = cache_class.refresh_data(identifier=slug) if slug == "global" else cache_class.refresh_data(slug)
    assert refreshed_data is not None, "Refresh data returned None"
    assert len(refreshed_data) > 0, "No data returned by refresh"
    assert sum(item["payments"] for item in refreshed_data) > 0, "Payments data mismatch"
    serializer_fields = DashboardBaseSerializer().get_fields()
    required_fields = {key for key, field in serializer_fields.items() if field.required}

    assert all(item.keys() >= required_fields for item in refreshed_data), f"Missing required fields in {cache_name}"
    assert all(item.keys() & expected_optional_fields == expected_optional_fields for item in refreshed_data), (
        f"Expected optional fields {expected_optional_fields} are missing in {cache_name}"
    )
    cached_data = cache.get(cache_key)
    assert cached_data is not None, "Data not cached"


# ============================================================================
# Non-Existent Business Area Tests
# ============================================================================


@pytest.mark.django_db
def test_refresh_data_non_existent_ba() -> None:
    slug = "non-existent-slug"
    cache_key = DashboardDataCache.get_cache_key(slug)
    cache.delete(cache_key)

    BusinessArea.objects.filter(slug=slug).delete()

    result = DashboardDataCache.refresh_data(slug)
    assert result == []
    cached_data = cache.get(cache_key)
    assert cached_data is not None
    assert json.loads(cached_data) == []


# ============================================================================
# No Payments Tests
# ============================================================================


@pytest.mark.django_db
def test_refresh_data_no_payments_ba(afghanistan: BusinessArea) -> None:
    Payment.objects.filter(
        program__business_area=afghanistan,
        parent__status__in=["ACCEPTED", "FINISHED"],
        program__is_visible=True,
        parent__is_removed=False,
        is_removed=False,
        conflicted=False,
        excluded=False,
    ).exclude(
        status__in=[
            "Transaction Erroneous",
            "Not Distributed",
            "Force failed",
            "Manually Cancelled",
        ]
    ).delete()

    cache_key = DashboardDataCache.get_cache_key(afghanistan.slug)
    cache.delete(cache_key)

    result = DashboardDataCache.refresh_data(afghanistan.slug)
    assert result == []
    cached_data = cache.get(cache_key)
    assert cached_data is not None
    assert json.loads(cached_data) == []


@pytest.mark.django_db
def test_refresh_data_no_payments_global() -> None:
    Payment.objects.filter(
        parent__status__in=["ACCEPTED", "FINISHED"],
        program__is_visible=True,
        parent__is_removed=False,
        is_removed=False,
        conflicted=False,
        excluded=False,
    ).exclude(
        status__in=[
            "Transaction Erroneous",
            "Not Distributed",
            "Force failed",
            "Manually Cancelled",
        ]
    ).delete()

    cache_key = DashboardGlobalDataCache.get_cache_key("global")
    cache.delete(cache_key)

    result = DashboardGlobalDataCache.refresh_data(identifier=GLOBAL_SLUG)
    assert result == []
    cached_data = cache.get(cache_key)
    assert cached_data is not None
    assert json.loads(cached_data) == []


# ============================================================================
# Partial Refresh Tests
# ============================================================================


@pytest.fixture
def partial_refresh_data_for_ba(afghanistan):
    ba_slug = afghanistan.slug
    cache.delete(DashboardDataCache.get_cache_key(ba_slug))

    prog = ProgramFactory(business_area=afghanistan)
    household = HouseholdFactory(program=prog, business_area=afghanistan)

    PaymentFactory(
        parent__status=PaymentPlan.Status.ACCEPTED,
        household=household,
        program=prog,
        business_area=afghanistan,
        delivery_date=timezone.datetime(CURRENT_YEAR - 1, 1, 1, tzinfo=dt_timezone.utc),
        delivered_quantity_usd=Decimal("100.00"),
    )
    PaymentFactory(
        parent__status=PaymentPlan.Status.ACCEPTED,
        household=household,
        program=prog,
        business_area=afghanistan,
        delivery_date=timezone.datetime(CURRENT_YEAR, 1, 1, tzinfo=dt_timezone.utc),
        delivered_quantity_usd=Decimal("200.00"),
    )

    return {
        "ba_slug": ba_slug,
        "afghanistan": afghanistan,
        "prog": prog,
        "household": household,
    }


@pytest.mark.django_db
def test_partial_refresh_empty_cache_fallback(partial_refresh_data_for_ba) -> None:
    data = partial_refresh_data_for_ba
    ba_slug = data["ba_slug"]

    refreshed_data = DashboardDataCache.refresh_data(ba_slug, years_to_refresh=[CURRENT_YEAR])

    assert len(refreshed_data) == 2, "Should contain data for both years due to full fallback"
    years_in_result = {item["year"] for item in refreshed_data}
    assert {CURRENT_YEAR, CURRENT_YEAR - 1} == years_in_result

    cache.delete(DashboardGlobalDataCache.get_cache_key(GLOBAL_SLUG))
    refreshed_global_data = DashboardGlobalDataCache.refresh_data(
        identifier=GLOBAL_SLUG, years_to_refresh=[CURRENT_YEAR]
    )
    assert len(refreshed_global_data) == 2
    global_years_in_result = {item["year"] for item in refreshed_global_data}
    assert {CURRENT_YEAR, CURRENT_YEAR - 1} == global_years_in_result


@pytest.fixture
def partial_refresh_combines_data_setup(afghanistan, fsp_common, delivery_mechanism_common):
    def _setup(is_global_scenario):
        if is_global_scenario:
            cache_identifier = GLOBAL_SLUG
            payment_ba = afghanistan
            prog = ProgramFactory(business_area=payment_ba)
            common_currency = "USD"
        else:
            payment_ba = BusinessAreaFactory()
            cache_identifier = payment_ba.slug
            prog = ProgramFactory(business_area=payment_ba)
            common_currency = "AFG"

        household = HouseholdFactory(program=prog, business_area=payment_ba, size=1)

        year_old = CURRENT_YEAR - 2
        year_mid = CURRENT_YEAR - 1
        year_new = CURRENT_YEAR

        PaymentFactory(
            parent__status=PaymentPlan.Status.ACCEPTED,
            household=household,
            program=prog,
            business_area=payment_ba,
            delivery_date=timezone.datetime(year_old, 1, 1, tzinfo=dt_timezone.utc),
            delivered_quantity_usd=Decimal("100.00"),
            status="Transaction Successful",
            financial_service_provider=fsp_common,
            delivery_type=delivery_mechanism_common,
            currency=common_currency,
        )

        return {
            "cache_identifier": cache_identifier,
            "payment_ba": payment_ba,
            "prog": prog,
            "household": household,
            "year_old": year_old,
            "year_mid": year_mid,
            "year_new": year_new,
            "is_global_scenario": is_global_scenario,
            "common_currency": common_currency,
            "fsp": fsp_common,
            "delivery_type": delivery_mechanism_common,
        }

    return _setup


@pytest.mark.parametrize(
    ("cache_class_under_test", "is_global_scenario"),
    [
        (DashboardGlobalDataCache, True),
        (DashboardDataCache, False),
    ],
)
@pytest.mark.django_db
def test_partial_refresh_combines_data(
    cache_class_under_test: Type[DashboardCacheBase],
    is_global_scenario: bool,
    partial_refresh_combines_data_setup,
) -> None:
    setup = partial_refresh_combines_data_setup(is_global_scenario)
    cache_identifier = setup["cache_identifier"]
    payment_ba = setup["payment_ba"]
    prog = setup["prog"]
    household = setup["household"]
    year_old = setup["year_old"]
    year_mid = setup["year_mid"]
    year_new = setup["year_new"]
    fsp = setup["fsp"]
    delivery_type = setup["delivery_type"]
    common_currency = setup["common_currency"]

    if is_global_scenario:
        cache_class_under_test.refresh_data(identifier=cache_identifier)
    else:
        cache_class_under_test.refresh_data(cache_identifier)
    cached_data_step1 = cache_class_under_test.get_data(cache_identifier)
    assert cached_data_step1 is not None, "cached_data_step1 should not be None after refresh"
    assert len(cached_data_step1) == 1
    assert cached_data_step1[0]["year"] == year_old
    assert Decimal(cached_data_step1[0]["total_delivered_quantity_usd"]) == Decimal("100.00")

    PaymentFactory(
        parent__status=PaymentPlan.Status.ACCEPTED,
        household=household,
        program=prog,
        business_area=payment_ba,
        delivery_date=timezone.datetime(year_mid, 1, 1, tzinfo=dt_timezone.utc),
        delivered_quantity_usd=Decimal("200.00"),
        status="Transaction Successful",
        financial_service_provider=fsp,
        delivery_type=delivery_type,
        currency=common_currency,
    )
    PaymentFactory(
        parent__status=PaymentPlan.Status.ACCEPTED,
        household=household,
        program=prog,
        business_area=payment_ba,
        delivery_date=timezone.datetime(year_new, 1, 1, tzinfo=dt_timezone.utc),
        delivered_quantity_usd=Decimal("300.00"),
        status="Transaction Successful",
        financial_service_provider=fsp,
        delivery_type=delivery_type,
        currency=common_currency,
    )

    if is_global_scenario:
        refreshed_data = cache_class_under_test.refresh_data(
            identifier=cache_identifier, years_to_refresh=[year_mid, year_new]
        )
    else:
        refreshed_data = cache_class_under_test.refresh_data(cache_identifier, years_to_refresh=[year_mid, year_new])

    assert refreshed_data is not None, "Refreshed data should not be None"
    assert len(refreshed_data) == 3, "Should contain data for all three years"

    data_map = {item["year"]: item for item in refreshed_data}
    assert Decimal(data_map[year_old]["total_delivered_quantity_usd"]) == Decimal("100.00")
    assert Decimal(data_map[year_mid]["total_delivered_quantity_usd"]) == Decimal("200.00")
    assert Decimal(data_map[year_new]["total_delivered_quantity_usd"]) == Decimal("300.00")


@pytest.fixture
def partial_refresh_global_no_new_payments_data(afghanistan):
    prog = ProgramFactory(business_area=afghanistan)
    household = HouseholdFactory(program=prog, business_area=afghanistan)

    year_cached = CURRENT_YEAR - 2
    PaymentFactory(
        parent__status=PaymentPlan.Status.ACCEPTED,
        household=household,
        program=prog,
        business_area=afghanistan,
        delivery_date=timezone.datetime(year_cached, 1, 1, tzinfo=dt_timezone.utc),
        delivered_quantity_usd=Decimal("50.00"),
    )
    DashboardGlobalDataCache.refresh_data(identifier=GLOBAL_SLUG)

    return {"year_cached": year_cached}


@pytest.mark.django_db
def test_partial_refresh_global_no_new_payments(partial_refresh_global_no_new_payments_data) -> None:
    data = partial_refresh_global_no_new_payments_data
    year_cached = data["year_cached"]

    cached_data_step1 = DashboardGlobalDataCache.get_data(GLOBAL_SLUG)
    assert cached_data_step1 is not None
    assert len(cached_data_step1) == 1
    assert cached_data_step1[0]["year"] == year_cached

    years_to_refresh_recent = [CURRENT_YEAR, CURRENT_YEAR - 1]
    refreshed_data = DashboardGlobalDataCache.refresh_data(
        identifier=GLOBAL_SLUG, years_to_refresh=years_to_refresh_recent
    )

    assert len(refreshed_data) == 1, "Should only contain the old cached data"
    assert refreshed_data[0]["year"] == year_cached
    assert Decimal(refreshed_data[0]["total_delivered_quantity_usd"]) == Decimal("50.00")


@pytest.fixture
def partial_refresh_ba_no_new_payments_data(afghanistan):
    ba_slug = afghanistan.slug
    prog = ProgramFactory(business_area=afghanistan)
    household = HouseholdFactory(program=prog, business_area=afghanistan)

    year_cached = CURRENT_YEAR - 2
    PaymentFactory(
        parent__status=PaymentPlan.Status.ACCEPTED,
        household=household,
        program=prog,
        business_area=afghanistan,
        delivery_date=timezone.datetime(year_cached, 1, 1, tzinfo=dt_timezone.utc),
        delivered_quantity_usd=Decimal("50.00"),
    )
    DashboardDataCache.refresh_data(ba_slug)

    return {"ba_slug": ba_slug, "year_cached": year_cached}


@pytest.mark.django_db
def test_partial_refresh_ba_no_new_payments(partial_refresh_ba_no_new_payments_data) -> None:
    data = partial_refresh_ba_no_new_payments_data
    ba_slug = data["ba_slug"]
    year_cached = data["year_cached"]

    years_to_refresh_recent = [CURRENT_YEAR, CURRENT_YEAR - 1]
    refreshed_data = DashboardDataCache.refresh_data(ba_slug, years_to_refresh=years_to_refresh_recent)

    assert len(refreshed_data) == 1, "Should only contain the old cached data"
    assert refreshed_data[0]["year"] == year_cached
    assert Decimal(refreshed_data[0]["total_delivered_quantity_usd"]) == Decimal("50.00")


@pytest.mark.django_db
def test_partial_refresh_ba_no_payments_at_all(afghanistan: BusinessArea) -> None:
    ba_slug = afghanistan.slug
    Payment.objects.filter(business_area=afghanistan).delete()
    cache.delete(DashboardDataCache.get_cache_key(ba_slug))

    years_to_refresh_recent = [CURRENT_YEAR, CURRENT_YEAR - 1]
    refreshed_data = DashboardDataCache.refresh_data(ba_slug, years_to_refresh=years_to_refresh_recent)

    assert refreshed_data == []
