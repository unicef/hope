import datetime
from typing import Any
from unittest.mock import MagicMock, patch

from django.utils import timezone
from freezegun import freeze_time
import pytest

from extras.test_utils.factories import (
    BusinessAreaFactory,
    HouseholdFactory,
    IndividualFactory,
    ProgramFactory,
    RegistrationDataImportFactory,
)
from hope.apps.household.celery_tasks import (
    interval_recalculate_population_fields_task_action,
    recalculate_population_fields_task_action,
)
from hope.apps.household.const import (
    AUNT_UNCLE,
    BROTHER_SISTER,
    COUSIN,
    FEMALE,
    GRANDDAUGHTER_GRANDSON,
    HEAD,
    MALE,
    NON_BENEFICIARY,
)
from hope.apps.household.services.household_recalculate_data import recalculate_data
from hope.models import AsyncJob, BusinessArea, Household, Individual

pytestmark = pytest.mark.django_db


def create_async_job(action: str, config: dict) -> AsyncJob:
    return AsyncJob.objects.create(
        type="JOB_TASK",
        action=action,
        config=config,
    )


@pytest.fixture
def business_area() -> BusinessArea:
    return BusinessAreaFactory(name="Afghanistan", slug="afghanistan", code="0060")


@pytest.fixture
def program(business_area: BusinessArea) -> Any:
    program = ProgramFactory(business_area=business_area)
    dct = program.data_collecting_type
    dct.recalculate_composition = True
    dct.save()
    return program


@pytest.fixture
def registration_data_import(business_area: BusinessArea, program: Any) -> Any:
    return RegistrationDataImportFactory(business_area=business_area, program=program)


@pytest.fixture
def household_with_individuals(
    business_area: BusinessArea, program: Any, registration_data_import: Any
) -> tuple[Household, list[Individual]]:
    household = HouseholdFactory(
        business_area=business_area,
        program=program,
        registration_data_import=registration_data_import,
        female_age_group_0_5_count=2,
        female_age_group_6_11_count=1,
        female_age_group_12_17_count=0,
        female_age_group_18_59_count=2,
        female_age_group_60_count=0,
        male_age_group_0_5_count=0,
        male_age_group_6_11_count=0,
        male_age_group_12_17_count=0,
        male_age_group_18_59_count=1,
        male_age_group_60_count=0,
        female_age_group_0_5_disabled_count=2,
        female_age_group_6_11_disabled_count=1,
        female_age_group_12_17_disabled_count=0,
        female_age_group_18_59_disabled_count=2,
        female_age_group_60_disabled_count=0,
        male_age_group_0_5_disabled_count=0,
        male_age_group_6_11_disabled_count=0,
        male_age_group_12_17_disabled_count=0,
        male_age_group_18_59_disabled_count=1,
        male_age_group_60_disabled_count=0,
        size=6,
        pregnant_count=2,
        fchild_hoh=True,
        child_hoh=False,
    )
    individuals_data = [
        {
            "relationship": COUSIN,
            "sex": FEMALE,
            "birth_date": datetime.date(1981, 8, 8),
            "pregnant": True,
            "physical_disability": "LOT_DIFFICULTY",
        },
        {
            "relationship": GRANDDAUGHTER_GRANDSON,
            "sex": FEMALE,
            "birth_date": datetime.date(1993, 9, 1),
            "pregnant": True,
            "selfcare_disability": "CANNOT_DO",
        },
        {
            "relationship": BROTHER_SISTER,
            "sex": FEMALE,
            "birth_date": datetime.date(2015, 7, 29),
            "pregnant": False,
            "seeing_disability": "LOT_DIFFICULTY",
            "hearing_disability": "LOT_DIFFICULTY",
            "physical_disability": "LOT_DIFFICULTY",
            "memory_disability": "LOT_DIFFICULTY",
            "selfcare_disability": "LOT_DIFFICULTY",
            "comms_disability": "LOT_DIFFICULTY",
        },
        {
            "relationship": AUNT_UNCLE,
            "sex": FEMALE,
            "birth_date": datetime.date(2009, 7, 29),
            "pregnant": False,
            "hearing_disability": "CANNOT_DO",
        },
        {
            "relationship": NON_BENEFICIARY,
            "sex": MALE,
            "birth_date": datetime.date(2015, 7, 29),
            "pregnant": False,
            "hearing_disability": "CANNOT_DO",
        },
        {
            "relationship": COUSIN,
            "sex": MALE,
            "birth_date": datetime.date(1961, 7, 29),
            "pregnant": False,
            "memory_disability": "LOT_DIFFICULTY",
            "comms_disability": "LOT_DIFFICULTY",
        },
    ]
    head = household.head_of_household
    head.relationship = HEAD
    head.sex = FEMALE
    head.birth_date = datetime.date(2021, 6, 29)
    head.pregnant = False
    head.memory_disability = "LOT_DIFFICULTY"
    head.registration_data_import = registration_data_import
    head.save()

    individuals = [head]
    for data in individuals_data:
        ind = IndividualFactory(
            household=household,
            business_area=business_area,
            program=program,
            registration_data_import=registration_data_import,
            first_registration_date=timezone.make_aware(datetime.datetime(2021, 1, 11)),
            **data,
        )
        individuals.append(ind)

    return household, individuals


@pytest.mark.parametrize(
    ("field", "expected"),
    [
        ("female_age_group_0_5_count", 1),
        ("female_age_group_6_11_count", 1),
        ("female_age_group_12_17_count", 1),
        ("female_age_group_18_59_count", 2),
        ("female_age_group_60_count", 0),
        ("male_age_group_0_5_count", 0),
        ("male_age_group_6_11_count", 0),
        ("male_age_group_12_17_count", 0),
        ("male_age_group_18_59_count", 0),
        ("male_age_group_60_count", 1),
        ("female_age_group_0_5_disabled_count", 1),
        ("female_age_group_6_11_disabled_count", 1),
        ("female_age_group_12_17_disabled_count", 1),
        ("female_age_group_18_59_disabled_count", 2),
        ("female_age_group_60_disabled_count", 0),
        ("male_age_group_0_5_disabled_count", 0),
        ("male_age_group_6_11_disabled_count", 0),
        ("male_age_group_12_17_disabled_count", 0),
        ("male_age_group_18_59_disabled_count", 0),
        ("male_age_group_60_disabled_count", 1),
        ("size", 6),
        ("pregnant_count", 2),
    ],
)
@freeze_time("2021-07-30")
def test_recalculate_field(household_with_individuals: tuple, field: str, expected: int) -> None:
    household, _ = household_with_individuals
    recalculate_data(household)
    household = Household.objects.get(pk=household.pk)
    assert getattr(household, field) == expected


@patch("hope.apps.household.celery_tasks.recalculate_population_fields_task")
@freeze_time("2021-07-29")
def test_interval_recalculate_population_fields_task(
    recalculate_population_fields_task_mock: MagicMock,
    household_with_individuals: tuple,
) -> None:
    household, _ = household_with_individuals
    job = create_async_job(
        "hope.apps.household.celery_tasks.interval_recalculate_population_fields_task_action",
        {},
    )
    interval_recalculate_population_fields_task_action(job)
    recalculate_population_fields_task_mock.assert_called_once_with(household_ids=[str(household.pk)])


@freeze_time("2021-07-30")
def test_recalculate_population_fields_task(household_with_individuals: tuple) -> None:
    household, _ = household_with_individuals
    job = create_async_job(
        "hope.apps.household.celery_tasks.recalculate_population_fields_task_action",
        {"household_ids": [str(household.pk)], "program_id": str(household.program_id)},
    )
    recalculate_population_fields_task_action(job)
    household = Household.objects.get(pk=household.pk)
    assert household.size == 6


@freeze_time("2021-07-30")
def test_recalculation_for_last_registration_date(
    business_area: BusinessArea, program: Any, registration_data_import: Any
) -> None:
    household = HouseholdFactory(
        business_area=business_area,
        program=program,
        registration_data_import=registration_data_import,
    )
    head = household.head_of_household
    head.relationship = HEAD
    head.sex = FEMALE
    head.birth_date = datetime.date(2022, 1, 1)
    head.pregnant = False
    head.memory_disability = "LOT_DIFFICULTY"
    head.registration_data_import = registration_data_import
    head.save()

    individuals_data = [
        {
            "relationship": COUSIN,
            "sex": FEMALE,
            "birth_date": datetime.date(1981, 1, 1),
            "pregnant": True,
            "physical_disability": "LOT_DIFFICULTY",
        },
        {
            "relationship": GRANDDAUGHTER_GRANDSON,
            "sex": FEMALE,
            "birth_date": datetime.date(1993, 1, 1),
            "pregnant": True,
            "selfcare_disability": "CANNOT_DO",
        },
        {
            "relationship": BROTHER_SISTER,
            "sex": FEMALE,
            "birth_date": datetime.date(2000, 1, 1),
            "pregnant": False,
            "seeing_disability": "LOT_DIFFICULTY",
            "hearing_disability": "LOT_DIFFICULTY",
            "physical_disability": "LOT_DIFFICULTY",
            "memory_disability": "LOT_DIFFICULTY",
            "selfcare_disability": "LOT_DIFFICULTY",
            "comms_disability": "LOT_DIFFICULTY",
        },
        {
            "relationship": AUNT_UNCLE,
            "sex": FEMALE,
            "birth_date": datetime.date(2009, 1, 1),
            "pregnant": False,
            "hearing_disability": "CANNOT_DO",
        },
        {
            "relationship": NON_BENEFICIARY,
            "sex": MALE,
            "birth_date": datetime.date(2020, 1, 1),
            "pregnant": False,
            "hearing_disability": "CANNOT_DO",
        },
        {
            "relationship": COUSIN,
            "sex": MALE,
            "birth_date": datetime.date(1955, 1, 1),
            "pregnant": False,
            "memory_disability": "LOT_DIFFICULTY",
            "comms_disability": "LOT_DIFFICULTY",
        },
    ]
    for data in individuals_data:
        IndividualFactory(
            household=household,
            business_area=business_area,
            program=program,
            registration_data_import=registration_data_import,
            **data,
        )

    household.last_registration_date = timezone.make_aware(datetime.datetime(2023, 1, 2))
    household.save()

    recalculate_data(household=household, save=True)
    household.refresh_from_db()

    assert household.size == 6
    assert household.female_age_group_0_5_count == 1
    assert household.male_age_group_0_5_count == 0  # NON_BENEFICIARY
    assert household.female_age_group_12_17_count == 1
    assert household.female_age_group_18_59_count == 3
    assert household.male_age_group_60_count == 1
    assert household.pregnant_count == 2
    assert household.female_age_group_0_5_disabled_count == 1
    assert household.female_age_group_12_17_disabled_count == 1
    assert household.female_age_group_18_59_disabled_count == 3
    assert household.children_count == 2
    assert household.female_children_count == 2
    assert household.children_disabled_count == 2
    assert household.female_children_disabled_count == 2
