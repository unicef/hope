from datetime import timezone as dt_timezone
import json
from typing import Any, Optional
from unittest.mock import patch

from django.core.cache import cache
from django.utils import timezone
import pytest

from extras.test_utils.factories import (
    BeneficiaryGroupFactory,
    BusinessAreaFactory,
    CountryFactory,
    DataCollectingTypeFactory,
    HouseholdFactory,
    PaymentFactory,
    PaymentPlanFactory,
    PaymentVerificationPlanFactory,
    PaymentVerificationSummaryFactory,
    ProgramCycleFactory,
    ProgramFactory,
)
from hope.apps.dashboard.services import (
    GLOBAL_SLUG,
    DashboardCacheBase,
    DashboardDataCache,
    DashboardGlobalDataCache,
    get_fertility_rate,
    get_pwd_count_expression,
)
from hope.models import Household, Payment, PaymentPlan


@pytest.fixture
def use_default_db_for_dashboard():
    with (
        patch("hope.apps.dashboard.services.settings.DASHBOARD_DB", "default"),
        patch("hope.apps.dashboard.celery_tasks.settings.DASHBOARD_DB", "default"),
    ):
        yield


pytestmark = pytest.mark.usefixtures("use_default_db_for_dashboard")

CURRENT_YEAR = timezone.now().year
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
def create_verification_plan_with_status(db):
    def _create(payment_plan, status):
        if not hasattr(payment_plan, "payment_verification_summary"):
            PaymentVerificationSummaryFactory(payment_plan=payment_plan)
        pvp = PaymentVerificationPlanFactory(payment_plan=payment_plan)
        pvp.status = status
        pvp.save(update_fields=["status"])
        return pvp

    return _create


# ============================================================================
# PWD Count Expression Tests
# ============================================================================


@pytest.fixture
def households_for_pwd_test(db):
    ba = BusinessAreaFactory()
    hh_zero_pwd = HouseholdFactory(
        business_area=ba,
        female_age_group_0_5_disabled_count=0,
        female_age_group_6_11_disabled_count=0,
        female_age_group_12_17_disabled_count=0,
        female_age_group_18_59_disabled_count=0,
        female_age_group_60_disabled_count=0,
        male_age_group_0_5_disabled_count=0,
        male_age_group_6_11_disabled_count=0,
        male_age_group_12_17_disabled_count=0,
        male_age_group_18_59_disabled_count=0,
        male_age_group_60_disabled_count=0,
    )
    hh_some_pwd = HouseholdFactory(
        business_area=ba,
        female_age_group_0_5_disabled_count=1,
        female_age_group_6_11_disabled_count=None,
        female_age_group_12_17_disabled_count=2,
        male_age_group_18_59_disabled_count=3,
        male_age_group_60_disabled_count=None,
    )
    hh_all_none = HouseholdFactory(
        business_area=ba,
        female_age_group_0_5_disabled_count=None,
        female_age_group_6_11_disabled_count=None,
        female_age_group_12_17_disabled_count=None,
        female_age_group_18_59_disabled_count=None,
        female_age_group_60_disabled_count=None,
        male_age_group_0_5_disabled_count=None,
        male_age_group_6_11_disabled_count=None,
        male_age_group_12_17_disabled_count=None,
        male_age_group_18_59_disabled_count=None,
        male_age_group_60_disabled_count=None,
    )
    return hh_zero_pwd, hh_some_pwd, hh_all_none


@pytest.mark.parametrize(
    ("household_index", "expected_pwd_count"),
    [
        (0, 0),  # hh_zero_pwd
        (1, 6),  # hh_some_pwd (1 + 2 + 3)
        (2, 0),  # hh_all_none
    ],
    ids=["zero_pwds", "some_pwds", "all_none"],
)
@pytest.mark.django_db
def test_pwd_count_expression(household_index: int, expected_pwd_count: int, households_for_pwd_test) -> None:
    hh_zero_pwd, hh_some_pwd, hh_all_none = households_for_pwd_test
    households = [hh_zero_pwd, hh_some_pwd, hh_all_none]
    target_household = households[household_index]

    hh_annotated = (
        Household.objects.filter(id=target_household.id)
        .annotate(calculated_pwd_count=get_pwd_count_expression())
        .first()
    )

    assert hh_annotated.calculated_pwd_count == expected_pwd_count


# ============================================================================
# Payment Plan Counts Tests
# ============================================================================


@pytest.fixture
def payment_plan_counts_data(create_verification_plan_with_status, db):
    ba = BusinessAreaFactory()
    prog_a_sector_x = ProgramFactory(business_area=ba, sector="SectorX", name="ProgramA")
    prog_b_sector_y = ProgramFactory(business_area=ba, sector="SectorY", name="ProgramB")

    cycle_a1 = ProgramCycleFactory(program=prog_a_sector_x, title="Cycle A1")
    cycle_a2 = ProgramCycleFactory(program=prog_a_sector_x, title="Cycle A2")
    cycle_a3 = ProgramCycleFactory(program=prog_a_sector_x, title="Cycle A3")
    cycle_a4 = ProgramCycleFactory(program=prog_a_sector_x, title="Cycle A4")
    cycle_b1 = ProgramCycleFactory(program=prog_b_sector_y, title="Cycle B1")

    pp1 = PaymentPlanFactory(program_cycle=cycle_a1, business_area=ba)
    pp2 = PaymentPlanFactory(program_cycle=cycle_a2, business_area=ba)
    pp3 = PaymentPlanFactory(program_cycle=cycle_b1, business_area=ba)
    pp4 = PaymentPlanFactory(program_cycle=cycle_a3, business_area=ba)
    pp5 = PaymentPlanFactory(program_cycle=cycle_a4, business_area=ba)

    create_verification_plan_with_status(pp2, "FINISHED")
    create_verification_plan_with_status(pp4, "FINISHED")

    PaymentFactory(
        parent=pp1,
        program=prog_a_sector_x,
        business_area=ba,
        delivery_date=timezone.datetime(2023, 1, 10, tzinfo=dt_timezone.utc),
    )
    PaymentFactory(
        parent=pp2,
        program=prog_a_sector_x,
        business_area=ba,
        delivery_date=timezone.datetime(2023, 6, 1, tzinfo=dt_timezone.utc),
    )
    PaymentFactory(
        parent=pp3,
        program=prog_b_sector_y,
        business_area=ba,
        delivery_date=timezone.datetime(2023, 3, 10, tzinfo=dt_timezone.utc),
    )
    PaymentFactory(
        parent=pp4,
        program=prog_a_sector_x,
        business_area=ba,
        delivery_date=timezone.datetime(2024, 6, 1, tzinfo=dt_timezone.utc),
    )
    PaymentFactory(
        parent=pp5,
        program=prog_a_sector_x,
        business_area=ba,
        delivery_date=timezone.datetime(2023, 1, 15, tzinfo=dt_timezone.utc),
    )

    return {
        "ba": ba,
        "prog_a": prog_a_sector_x,
        "prog_b": prog_b_sector_y,
        "pp1": pp1,
        "pp2": pp2,
        "pp3": pp3,
        "pp4": pp4,
        "pp5": pp5,
    }


@pytest.mark.django_db
def test_payment_plan_counts(payment_plan_counts_data) -> None:
    data = payment_plan_counts_data
    ba = data["ba"]

    base_payments_qs = Payment.objects.filter(business_area=ba)
    group_by_fields = ["year", "sector_name"]

    result = DashboardCacheBase._get_payment_plan_counts(base_payments_qs, group_by_fields)

    expected_total_counts = {
        (2023, "SectorX"): 3,
        (2023, "SectorY"): 1,
        (2024, "SectorX"): 1,
    }
    expected_finished_counts = {
        (2023, "SectorX"): 1,
        (2024, "SectorX"): 1,
    }

    assert result["total"] == expected_total_counts, "Total payment plan counts mismatch"
    assert result["finished"] == expected_finished_counts, "Finished payment plan counts mismatch"

    group_by_fields_program = ["year", "program_name"]
    result_program_grouping = DashboardCacheBase._get_payment_plan_counts(base_payments_qs, group_by_fields_program)

    expected_total_program = {
        (2023, "ProgramA"): 3,
        (2023, "ProgramB"): 1,
        (2024, "ProgramA"): 1,
    }
    expected_finished_program = {
        (2023, "ProgramA"): 1,
        (2024, "ProgramA"): 1,
    }
    assert result_program_grouping["total"] == expected_total_program, "Total plan counts mismatch (program grouping)"
    assert result_program_grouping["finished"] == expected_finished_program, "Finished plan counts (program grouping)"

    empty_plan_qs = Payment.objects.filter(pk__in=[])
    result_empty = DashboardCacheBase._get_payment_plan_counts(empty_plan_qs, group_by_fields)
    assert result_empty["total"] == {}, "Expected empty total counts for no plans"
    assert result_empty["finished"] == {}, "Expected empty finished counts for no plans"


# ============================================================================
# Individuals Count Calculation Tests
# ============================================================================


@pytest.fixture
def individuals_count_test_data(afghanistan):
    def _create(test_id, dct_type, household_size, expected_individuals):
        cache.delete(DashboardDataCache.get_cache_key(afghanistan.slug))
        cache.delete(DashboardGlobalDataCache.get_cache_key(GLOBAL_SLUG))

        dct = DataCollectingTypeFactory(type=dct_type)
        beneficiary_group = BeneficiaryGroupFactory(master_detail=(dct_type != "SOCIAL"))
        program = ProgramFactory(
            business_area=afghanistan,
            data_collecting_type=dct,
            beneficiary_group=beneficiary_group,
            sector=f"Sector-{test_id}",
        )
        household = HouseholdFactory(
            program=program,
            business_area=afghanistan,
            size=household_size,
        )

        status_map = {
            "social_program_size": Payment.STATUS_SUCCESS,
            "standard_program_size": Payment.STATUS_DISTRIBUTION_SUCCESS,
        }
        status = status_map[test_id]

        PaymentFactory(
            household=household,
            program=program,
            business_area=afghanistan,
            delivery_date=TEST_DATE,
            parent__status=PaymentPlan.Status.ACCEPTED,
            status=status,
        )

        return {
            "afghanistan": afghanistan,
            "test_id": test_id,
            "expected_individuals": expected_individuals,
            "status": status,
        }

    return _create


@pytest.mark.parametrize(
    ("test_id", "dct_type", "household_size", "expected_individuals"),
    [
        ("social_program_size", "SOCIAL", 5, 1),
        ("standard_program_size", "STANDARD", 5, 5),
    ],
    ids=["social_program_size", "standard_program_size"],
)
@pytest.mark.django_db
def test_individuals_count_calculation_scenarios(
    test_id: str,
    dct_type: str,
    household_size: int,
    expected_individuals: int,
    individuals_count_test_data,
) -> None:
    data = individuals_count_test_data(test_id, dct_type, household_size, expected_individuals)

    result = DashboardDataCache.refresh_data(data["afghanistan"].slug)
    assert len(result) == 1
    assert result[0]["individuals"] == expected_individuals, "Country dashboard individuals count mismatch"

    global_result = DashboardGlobalDataCache.refresh_data(identifier=GLOBAL_SLUG)
    global_agg_group = [
        item
        for item in global_result
        if (
            item["country"] == data["afghanistan"].name
            and item["sector"] == f"Sector-{test_id}"
            and item["status"] == data["status"]
        )
    ]
    assert len(global_agg_group) == 1
    assert global_agg_group[0]["individuals"] == expected_individuals, "Global dashboard individuals count mismatch"


# ============================================================================
# Children Count Calculation Tests
# ============================================================================


@pytest.fixture
def children_count_test_data(afghanistan, mocker):
    def _create(test_id, dct_type, household_children_count, fertility_rate, expected_children):
        mocker.patch("hope.apps.dashboard.services.get_fertility_rate", return_value=fertility_rate)
        cache.delete(DashboardDataCache.get_cache_key(afghanistan.slug))
        cache.delete(DashboardGlobalDataCache.get_cache_key(GLOBAL_SLUG))

        dct = DataCollectingTypeFactory(type=dct_type)
        beneficiary_group = BeneficiaryGroupFactory(master_detail=(dct_type != "SOCIAL"))
        program = ProgramFactory(
            business_area=afghanistan,
            data_collecting_type=dct,
            beneficiary_group=beneficiary_group,
            sector=f"Sector-{test_id}",
        )
        household = HouseholdFactory(
            program=program,
            business_area=afghanistan,
            children_count=household_children_count,
        )

        status_map = {
            "social_program_with_value": Payment.STATUS_SUCCESS,
            "social_program_none": Payment.STATUS_SENT_TO_FSP,
            "standard_program_none": Payment.STATUS_DISTRIBUTION_SUCCESS,
            "standard_program_with_value": Payment.STATUS_PENDING,
        }
        status = status_map[test_id]

        PaymentFactory(
            household=household,
            program=program,
            business_area=afghanistan,
            delivery_date=TEST_DATE,
            status=status,
            parent__status=PaymentPlan.Status.ACCEPTED,
        )

        return {
            "afghanistan": afghanistan,
            "test_id": test_id,
            "expected_children": expected_children,
            "status": status,
        }

    return _create


@pytest.mark.parametrize(
    ("test_id", "dct_type", "household_children_count", "fertility_rate", "expected_children"),
    [
        ("social_program_with_value", "SOCIAL", 10, 0, 0),
        ("social_program_none", "SOCIAL", None, 0, 0),
        ("standard_program_none", "STANDARD", None, 3.8, 4),
        ("standard_program_with_value", "STANDARD", 7, 0, 7),
    ],
    ids=[
        "social_program_with_value",
        "social_program_none",
        "standard_program_none",
        "standard_program_with_value",
    ],
)
@pytest.mark.django_db
def test_children_count_calculation_scenarios(
    test_id: str,
    dct_type: str,
    household_children_count: Optional[int],
    fertility_rate: float,
    expected_children: int,
    children_count_test_data,
) -> None:
    data = children_count_test_data(test_id, dct_type, household_children_count, fertility_rate, expected_children)

    result = DashboardDataCache.refresh_data(data["afghanistan"].slug)
    assert len(result) == 1
    assert result[0]["children_counts"] == expected_children

    global_result = DashboardGlobalDataCache.refresh_data(identifier=GLOBAL_SLUG)
    global_agg_group = [
        item
        for item in global_result
        if (
            item["country"] == data["afghanistan"].name
            and item["sector"] == f"Sector-{data['test_id']}"
            and item["status"] == data["status"]
        )
    ]
    assert len(global_agg_group) == 1
    assert global_agg_group[0]["children_counts"] == expected_children


# ============================================================================
# Fertility Rate Tests
# ============================================================================


@pytest.fixture
def afghanistan_with_country(db):
    ba = BusinessAreaFactory(name="Afghanistan")
    country = CountryFactory(name="Afghanistan", short_name="AFG", iso_code2="AF", iso_code3="AFG", iso_num="0004")
    ba.countries.add(country)
    cache.delete("fertility_data")
    return ba


@pytest.mark.django_db
def test_get_fertility_rate_success(afghanistan_with_country, mocker: Any) -> None:
    rate = get_fertility_rate("Afghanistan", 2020)
    assert rate == 5.145
    mock_open = mocker.patch("builtins.open")
    rate2 = get_fertility_rate("Afghanistan", 2021)
    assert rate2 == 5.039
    mock_open.assert_not_called()


@pytest.mark.django_db
def test_get_fertility_rate_fallback_to_latest_year(afghanistan_with_country) -> None:
    rate = get_fertility_rate("Afghanistan", 2025)
    assert rate == 4.84


@pytest.mark.django_db
def test_get_fertility_rate_country_not_found() -> None:
    cache.delete("fertility_data")
    rate = get_fertility_rate("Wonderland", 2023)
    assert rate == 0.0


@pytest.mark.django_db
def test_get_fertility_rate_no_data(mocker: Any) -> None:
    mocker.patch("builtins.open", mocker.mock_open(read_data="[]"))
    cache.delete("fertility_data")
    rate = get_fertility_rate("AnyCountry", 2023)
    assert rate == 0.0


@pytest.mark.django_db
def test_load_fertility_data_file_not_found(mocker: Any) -> None:
    mock_sentry = mocker.patch("hope.apps.dashboard.services.sentry_sdk")
    mocker.patch("builtins.open", side_effect=FileNotFoundError("File not found"))
    cache.delete("fertility_data")

    with pytest.raises(FileNotFoundError):
        get_fertility_rate("AnyCountry", 2023)
    mock_sentry.capture_exception.assert_called_once()


@pytest.mark.django_db
def test_load_fertility_data_json_decode_error(mocker: Any) -> None:
    mock_sentry = mocker.patch("hope.apps.dashboard.services.sentry_sdk")
    mocker.patch("builtins.open", mocker.mock_open(read_data="invalid json"))
    cache.delete("fertility_data")

    with pytest.raises(json.JSONDecodeError):
        get_fertility_rate("AnyCountry", 2023)
    mock_sentry.capture_exception.assert_called_once()
