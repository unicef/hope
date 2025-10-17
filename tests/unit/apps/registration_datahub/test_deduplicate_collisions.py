from typing import Any

import pytest

from extras.test_utils.factories.core import create_afghanistan
from extras.test_utils.factories.household import create_household_and_individuals
from extras.test_utils.factories.program import ProgramFactory
from extras.test_utils.factories.registration_data import RegistrationDataImportFactory
from hope.apps.geo.models import Country
from hope.apps.household.models import Household, PendingIndividual
from hope.apps.program.collision_detectors import IdentificationKeyCollisionDetector
from hope.apps.program.models import Program
from hope.apps.registration_data.models import RegistrationDataImport
from hope.apps.registration_datahub.tasks.deduplicate import DeduplicateTask

pytestmark = pytest.mark.django_db(transaction=True)


@pytest.fixture
def poland() -> Country:
    return Country.objects.create(name="Poland", iso_code2="PL", iso_code3="POL", iso_num="616")


@pytest.fixture
def program(poland: Country) -> Program:
    business_area = create_afghanistan()
    business_area.countries.add(poland)
    program = ProgramFactory.create(
        name="Test Program for Deduplication",
        status=Program.ACTIVE,
        business_area=business_area,
    )
    program.collision_detection_enabled = True
    program.collision_detector = IdentificationKeyCollisionDetector
    program.save()
    return program


@pytest.fixture
def importing_registration_data_import(program: Program) -> RegistrationDataImport:
    return RegistrationDataImportFactory.create(
        program=program,
        business_area=program.business_area,
        status=RegistrationDataImport.IMPORTING,
    )


@pytest.fixture
def registration_data_import_merged(program: Program) -> RegistrationDataImport:
    return RegistrationDataImportFactory.create(
        program=program,
        business_area=program.business_area,
        status=RegistrationDataImport.MERGED,
    )


@pytest.fixture
def merged_household(
    program: Program, registration_data_import_merged: RegistrationDataImport
) -> tuple[Household, PendingIndividual]:
    household, inds = create_household_and_individuals(
        household_data={
            "program": program,
            "business_area": program.business_area,
            "registration_data_import": registration_data_import_merged,
            "identification_key": "COLLISION-KEY-001",
        },
        individuals_data=[
            {
                "registration_data_import": registration_data_import_merged,
                "business_area": program.business_area,
                "program": program,
                "identification_key": "IND-KEY-2",
                "rdi_merge_status": Household.PENDING,
            }
        ],
    )
    return (household, PendingIndividual.objects.get(pk=inds[0].pk))


@pytest.fixture
def pending_household(
    program: Program, importing_registration_data_import: RegistrationDataImport
) -> tuple[Household, PendingIndividual]:
    household, inds = create_household_and_individuals(
        household_data={
            "program": program,
            "business_area": program.business_area,
            "registration_data_import": importing_registration_data_import,
            "identification_key": "COLLISION-KEY-001",
            "rdi_merge_status": Household.PENDING,
        },
        individuals_data=[
            {
                "registration_data_import": importing_registration_data_import,
                "business_area": program.business_area,
                "program": program,
                "identification_key": "IND-KEY-2",
                "rdi_merge_status": Household.PENDING,
            }
        ],
    )
    return (household, PendingIndividual.objects.get(pk=inds[0].pk))


def test_collided_individuals_ids_to_exclude(
    merged_household: tuple[Household, PendingIndividual],
    pending_household: tuple[Household, PendingIndividual],
    importing_registration_data_import: RegistrationDataImport,
    program: Program,
) -> None:
    (merged_household1, merged_individual1) = merged_household
    (pending_household1, pending_individual1) = pending_household
    task = DeduplicateTask(program.business_area.slug, program.id)
    ids_to_exclude = task.collided_individuals_ids_to_exclude(
        PendingIndividual.objects.filter(registration_data_import=importing_registration_data_import),
        importing_registration_data_import,
    )
    assert str(pending_individual1.id) in ids_to_exclude


def test_deduplicate_pending_individuals_skips_collided(
    merged_household: tuple[Household, PendingIndividual],
    pending_household: tuple[Household, PendingIndividual],
    importing_registration_data_import: RegistrationDataImport,
    program: Program,
    mocker: Any,
) -> None:
    (merged_household1, merged_individual1) = merged_household
    (pending_household1, pending_individual1) = pending_household
    # Patch _deduplicate_single_individual to check if it's called
    task = DeduplicateTask(program.business_area.slug, program.id)
    spy = mocker.spy(task, "_deduplicate_single_individual")
    task.deduplicate_pending_individuals(importing_registration_data_import)
    # Should not be called for collided individuals
    assert spy.call_count == 0
