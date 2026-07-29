import datetime
from typing import Callable

from django.core.management import call_command
from django.utils import timezone
import pytest

from extras.test_utils.factories import (
    BusinessAreaFactory,
    HouseholdFactory,
    IndividualFactory,
    ProgramFactory,
)
from hope.apps.household.const import (
    COUSIN,
    DISABLED,
    FEMALE,
    HEAD,
    MALE,
    NON_BENEFICIARY,
    NOT_COLLECTED,
    OTHER,
)
from hope.apps.household.services.household_recalculate_data import (
    _aggregate_composition,
    aggregate_composition_by_household_id,
)
from hope.models import BusinessArea, Household

pytestmark = pytest.mark.django_db


@pytest.fixture
def business_area() -> BusinessArea:
    return BusinessAreaFactory()


@pytest.fixture
def make_household(business_area: BusinessArea) -> Callable[..., Household]:
    def _make(collects_individual_data: bool, **hh_kwargs: object) -> Household:
        program = ProgramFactory(business_area=business_area)
        dct = program.data_collecting_type
        dct.recalculate_composition = False
        dct.collects_individual_data = collects_individual_data
        dct.save()
        return HouseholdFactory(business_area=business_area, program=program, **hh_kwargs)

    return _make


@pytest.fixture
def household_present(make_household: Callable[..., Household]) -> Household:
    return make_household(collects_individual_data=False, female_age_group_0_5_count=3, size=7)


@pytest.fixture
def household_from_individuals(make_household: Callable[..., Household]) -> Household:
    household = make_household(collects_individual_data=True)
    household.last_registration_date = timezone.make_aware(datetime.datetime(2024, 1, 1))
    household.save(update_fields=["last_registration_date"])
    head = household.head_of_household
    head.relationship = HEAD
    head.sex = FEMALE
    head.birth_date = datetime.date(2020, 1, 1)
    head.save()
    IndividualFactory(
        household=household,
        business_area=household.business_area,
        program=household.program,
        registration_data_import=household.registration_data_import,
        relationship=COUSIN,
        sex=FEMALE,
        birth_date=datetime.date(2000, 1, 1),
    )
    return household


@pytest.fixture
def household_untouched(make_household: Callable[..., Household]) -> Household:
    # composition absent AND DCT does not collect individual data -> stays NULL
    return make_household(collects_individual_data=False)


def test_backfill_copies_stored_composition(household_present: Household) -> None:
    call_command("backfill_kab")
    household_present.refresh_from_db()

    assert household_present.kab_female_age_group_0_5_count == 3
    assert household_present.kab_size == 7


def test_backfill_computes_from_individuals(household_from_individuals: Household) -> None:
    call_command("backfill_kab", batch_size=1)
    household_from_individuals.refresh_from_db()

    assert household_from_individuals.kab_size == 2  # head + one cousin
    assert household_from_individuals.kab_female_age_group_0_5_count == 1


def test_backfill_leaves_unmatched_household_null(household_untouched: Household) -> None:
    call_command("backfill_kab")
    household_untouched.refresh_from_db()

    assert household_untouched.kab_size is None


def test_backfill_is_idempotent(household_present: Household) -> None:
    call_command("backfill_kab")
    call_command("backfill_kab")
    household_present.refresh_from_db()

    assert household_present.kab_size == 7


@pytest.fixture
def household_already_computed(make_household: Callable[..., Household]) -> Household:
    # composition absent, DCT collects individuals, but kab_size already set -> phase 2 must skip it
    return make_household(collects_individual_data=True, kab_size=99)


def test_backfill_skips_already_computed_household(household_already_computed: Household) -> None:
    call_command("backfill_kab")
    household_already_computed.refresh_from_db()

    assert household_already_computed.kab_size == 99


def test_backfill_compute_query_count_is_constant_per_batch(
    household_from_individuals: Household, django_assert_num_queries: object
) -> None:
    # programs list + empty phase-1 fetch + phase-2 pk fetch + grouped aggregate + bulk_update + empty next-batch fetch
    with django_assert_num_queries(6):
        call_command("backfill_kab")
    household_from_individuals.refresh_from_db()

    assert household_from_individuals.kab_size == 2


def test_backfill_copy_query_count_is_constant_per_batch(
    household_present: Household, django_assert_num_queries: object
) -> None:
    # programs list + phase-1 pk fetch + set-based copy UPDATE + empty next-batch fetch
    with django_assert_num_queries(4):
        call_command("backfill_kab")
    household_present.refresh_from_db()

    assert household_present.kab_size == 7


@pytest.fixture
def household_boundary_cases(make_household: Callable[..., Household]) -> Household:
    """Every counter dimension plus birth dates exactly on the 6/18/60-year cutoffs,
    so any divergence between the Python-date and SQL-interval cutoff arithmetic shows up."""
    household = make_household(collects_individual_data=True)
    household.last_registration_date = timezone.make_aware(datetime.datetime(2024, 1, 1))
    household.save(update_fields=["last_registration_date"])

    head = household.head_of_household
    head.relationship = HEAD
    head.sex = FEMALE
    head.birth_date = datetime.date(2018, 1, 1)  # exactly 6 years before last_registration_date
    head.withdrawn = False
    head.duplicate = False
    head.save()

    common = {
        "household": household,
        "business_area": household.business_area,
        "program": household.program,
        "registration_data_import": household.registration_data_import,
        "withdrawn": False,
        "duplicate": False,
    }
    IndividualFactory(**common, relationship=COUSIN, sex=MALE, birth_date=datetime.date(2006, 1, 1))  # exactly 18y
    IndividualFactory(**common, relationship=COUSIN, sex=FEMALE, birth_date=datetime.date(1964, 1, 1))  # exactly 60y
    IndividualFactory(
        **{**common, "disability": DISABLED}, relationship=COUSIN, sex=FEMALE, birth_date=datetime.date(2015, 1, 1)
    )
    IndividualFactory(**common, relationship=COUSIN, sex=FEMALE, birth_date=datetime.date(1990, 1, 1), pregnant=True)
    IndividualFactory(**common, relationship=NON_BENEFICIARY, sex=OTHER, birth_date=datetime.date(1990, 1, 1))
    IndividualFactory(
        **{**common, "withdrawn": True}, relationship=COUSIN, sex=NOT_COLLECTED, birth_date=datetime.date(1990, 1, 1)
    )
    IndividualFactory(
        **{**common, "duplicate": True}, relationship=COUSIN, sex=MALE, birth_date=datetime.date(1990, 1, 1)
    )
    return household


def test_batch_aggregate_matches_per_household_aggregate(household_boundary_cases: Household) -> None:
    batch = aggregate_composition_by_household_id([household_boundary_cases.pk])[household_boundary_cases.pk]

    assert batch == _aggregate_composition(household_boundary_cases)


def test_backfill_result_matches_recalculate_aggregate(household_boundary_cases: Household) -> None:
    call_command("backfill_kab")
    household_boundary_cases.refresh_from_db()

    expected = _aggregate_composition(household_boundary_cases)
    assert {field: getattr(household_boundary_cases, f"kab_{field}") for field in expected} == expected
