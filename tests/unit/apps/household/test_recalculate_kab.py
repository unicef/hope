import datetime
from typing import Any, Callable

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
    NOT_DISABLED,
)
from hope.apps.household.services.household_recalculate_data import (
    AGE_GROUP_FIELDS,
    KAB_SOURCE_FIELDS,
    _aggregate_composition,
    recalculate_data,
)
from hope.models import AsyncJob, BusinessArea, Household

pytestmark = pytest.mark.django_db


@pytest.fixture
def business_area() -> BusinessArea:
    return BusinessAreaFactory()


@pytest.fixture
def make_household(business_area: BusinessArea) -> Callable[..., Household]:
    def _make(recalculate_composition: bool, collects_individual_data: bool, **hh_kwargs: Any) -> Household:
        program = ProgramFactory(business_area=business_area)
        dct = program.data_collecting_type
        dct.recalculate_composition = recalculate_composition
        dct.collects_individual_data = collects_individual_data
        dct.save()
        return HouseholdFactory(business_area=business_area, program=program, **hh_kwargs)

    return _make


@pytest.fixture
def household_from_individuals(make_household: Callable[..., Household]) -> Callable[..., Household]:
    """Household with a known, controlled set of individuals and NO stored composition.

    Ages are measured against last_registration_date = 2024-01-01.
    Active beneficiaries: head (F, 0-5), A (M, 18-59), B (F, 6-11, disabled), D (F, 60+, pregnant).
    Excluded: C (non-beneficiary), E (withdrawn), F (duplicate).
    """

    def _make(recalculate_composition: bool, collects_individual_data: bool) -> Household:
        household = make_household(recalculate_composition, collects_individual_data)
        household.last_registration_date = timezone.make_aware(datetime.datetime(2024, 1, 1))
        household.save(update_fields=["last_registration_date"])

        program = household.program
        business_area = household.business_area
        common = {
            "household": household,
            "business_area": business_area,
            "program": program,
            "registration_data_import": household.registration_data_import,
            "withdrawn": False,
            "duplicate": False,
            "disability": NOT_DISABLED,
        }

        head = household.head_of_household
        head.relationship = HEAD
        head.sex = FEMALE
        head.birth_date = datetime.date(2020, 1, 1)
        head.pregnant = False
        head.disability = NOT_DISABLED
        head.withdrawn = False
        head.duplicate = False
        head.save()

        IndividualFactory(**common, relationship=COUSIN, sex=MALE, birth_date=datetime.date(2000, 1, 1))
        IndividualFactory(
            **{**common, "disability": DISABLED},
            relationship=COUSIN,
            sex=FEMALE,
            birth_date=datetime.date(2015, 1, 1),
        )
        IndividualFactory(**common, relationship=NON_BENEFICIARY, sex=MALE, birth_date=datetime.date(2020, 1, 1))
        IndividualFactory(
            **common, relationship=COUSIN, sex=FEMALE, birth_date=datetime.date(1950, 1, 1), pregnant=True
        )
        IndividualFactory(
            **{**common, "withdrawn": True}, relationship=COUSIN, sex=FEMALE, birth_date=datetime.date(2020, 1, 1)
        )
        IndividualFactory(
            **{**common, "duplicate": True}, relationship=COUSIN, sex=FEMALE, birth_date=datetime.date(2020, 1, 1)
        )
        return household

    return _make


def test_kab_source_fields_match_aggregate_keys(make_household: Callable[..., Household]) -> None:
    household = make_household(recalculate_composition=False, collects_individual_data=True)
    assert set(KAB_SOURCE_FIELDS) == set(_aggregate_composition(household).keys())
    assert set(AGE_GROUP_FIELDS) == {f for f in KAB_SOURCE_FIELDS if "_age_group_" in f}
    assert len(AGE_GROUP_FIELDS) == 20


def test_composition_present_mirrors_stored_values(make_household: Callable[..., Household]) -> None:
    # size=9 while only one individual exists -> proves stored values are mirrored, not counted.
    household = make_household(
        recalculate_composition=False,
        collects_individual_data=True,
        female_age_group_0_5_count=3,
        size=9,
    )

    recalculate_data(household)
    household.refresh_from_db()

    assert household.kab_female_age_group_0_5_count == 3
    assert household.kab_size == 9


def test_composition_present_mirrors_nulls_verbatim(make_household: Callable[..., Household]) -> None:
    household = make_household(
        recalculate_composition=False,
        collects_individual_data=True,
        female_age_group_0_5_count=2,
    )

    recalculate_data(household)
    household.refresh_from_db()

    assert household.kab_female_age_group_0_5_count == 2
    assert household.kab_female_age_group_6_11_count is None
    assert household.kab_size is None


@pytest.mark.parametrize(
    ("field", "expected"),
    [
        ("kab_size", 4),
        ("kab_female_age_group_0_5_count", 1),
        ("kab_male_age_group_18_59_count", 1),
        ("kab_female_age_group_6_11_count", 1),
        ("kab_female_age_group_60_count", 1),
        ("kab_female_age_group_6_11_disabled_count", 1),
        ("kab_male_age_group_18_59_disabled_count", 0),
        ("kab_pregnant_count", 1),
        ("kab_children_count", 2),
        ("kab_female_children_count", 2),
        ("kab_male_children_count", 0),
        ("kab_children_disabled_count", 1),
        ("kab_female_children_disabled_count", 1),
        ("kab_other_sex_group_count", 0),
        ("kab_unknown_sex_group_count", 0),
    ],
)
def test_composition_absent_computes_from_individuals(
    household_from_individuals: Callable[..., Household], field: str, expected: int
) -> None:
    household = household_from_individuals(recalculate_composition=False, collects_individual_data=True)

    recalculate_data(household)
    household.refresh_from_db()

    assert getattr(household, field) == expected


def test_composition_absent_does_not_touch_stored_size(
    household_from_individuals: Callable[..., Household],
) -> None:
    household = household_from_individuals(recalculate_composition=False, collects_individual_data=True)

    recalculate_data(household)
    household.refresh_from_db()

    assert household.kab_size == 4
    assert household.size is None
    assert household.female_age_group_0_5_count is None


def test_no_individual_data_keeps_kab_null(household_from_individuals: Callable[..., Household]) -> None:
    household = household_from_individuals(recalculate_composition=False, collects_individual_data=False)

    recalculate_data(household)
    household.refresh_from_db()

    assert household.kab_size is None
    assert all(getattr(household, f"kab_{field}") is None for field in KAB_SOURCE_FIELDS)


def test_recalculate_composition_true_populates_both(
    household_from_individuals: Callable[..., Household],
) -> None:
    household = household_from_individuals(recalculate_composition=True, collects_individual_data=True)

    recalculate_data(household)
    household.refresh_from_db()

    assert household.size == 4  # composition recomputed
    assert household.kab_size == 4  # KAB mirrors the freshly computed composition
    assert household.female_age_group_0_5_count == 1
    assert household.kab_female_age_group_0_5_count == 1


def test_run_from_migration_skips_individual_recalc(
    household_from_individuals: Callable[..., Household],
) -> None:
    household = household_from_individuals(recalculate_composition=True, collects_individual_data=True)

    # run_from_migration=True skips the per-individual recalculation but still aggregates composition + KAB.
    recalculate_data(household, run_from_migration=True)
    household.refresh_from_db()

    assert household.size == 4
    assert household.kab_size == 4


@pytest.mark.parametrize(
    ("sex", "birth_date", "expected_child_hoh", "expected_fchild_hoh"),
    [
        (FEMALE, datetime.date(2020, 1, 1), True, True),  # minor female head
        (MALE, datetime.date(2020, 1, 1), True, False),  # minor male head
        (FEMALE, datetime.date(1980, 1, 1), False, False),  # adult head
    ],
)
def test_child_hoh_flags_from_head(
    make_household: Callable[..., Household],
    sex: str,
    birth_date: datetime.date,
    expected_child_hoh: bool,
    expected_fchild_hoh: bool,
) -> None:
    household = make_household(recalculate_composition=True, collects_individual_data=False)
    household.last_registration_date = timezone.make_aware(datetime.datetime(2024, 1, 1))
    household.save(update_fields=["last_registration_date"])
    head = household.head_of_household
    head.relationship = HEAD
    head.sex = sex
    head.birth_date = birth_date
    head.save()

    recalculate_data(household)
    household.refresh_from_db()

    assert household.child_hoh is expected_child_hoh
    assert household.fchild_hoh is expected_fchild_hoh


def test_idempotent_on_flag_flip(household_from_individuals: Callable[..., Household]) -> None:
    household = household_from_individuals(recalculate_composition=False, collects_individual_data=True)
    recalculate_data(household)
    household.refresh_from_db()
    assert household.kab_size == 4

    dct = household.program.data_collecting_type
    dct.collects_individual_data = False
    dct.save()

    recalculate_data(household)
    household.refresh_from_db()
    assert household.kab_size is None


def test_async_task_populates_kab_for_non_recalculating_dct(
    household_from_individuals: Callable[..., Household],
    django_capture_on_commit_callbacks: Any,
) -> None:
    # Gate removal: previously the action emptied the queryset for recalculate_composition=False
    # DCTs, so nothing ran. Now the household flows to the chunk task and KAB is computed.
    household = household_from_individuals(recalculate_composition=False, collects_individual_data=True)
    job = AsyncJob.objects.create(
        type="JOB_TASK",
        action="hope.apps.household.celery_tasks.recalculate_population_fields_async_task_action",
        config={"household_ids": [str(household.pk)], "program_id": str(household.program_id)},
    )

    from hope.apps.household.celery_tasks import recalculate_population_fields_async_task_action

    with django_capture_on_commit_callbacks(execute=True):
        recalculate_population_fields_async_task_action(job)
    household.refresh_from_db()

    assert household.kab_size == 4
