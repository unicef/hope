from contextlib import contextmanager
from typing import Callable, Generator

from django.db import DEFAULT_DB_ALIAS, connections

import pytest
from extras.test_utils.factories.core import create_afghanistan
from extras.test_utils.factories.household import create_household_and_individuals
from extras.test_utils.factories.program import ProgramFactory
from extras.test_utils.factories.registration_data import RegistrationDataImportFactory

from hope.apps.geo.models import Area, AreaType, Country
from hope.apps.household.models import MALE, Household, Individual
from hope.apps.program.models import Program
from hope.apps.registration_data.models import RegistrationDataImport

pytestmark = [pytest.mark.usefixtures("django_elasticsearch_setup"), pytest.mark.elasticsearch, pytest.mark.django_db]


@contextmanager
def capture_on_commit_callbacks(
    *, using: str = DEFAULT_DB_ALIAS, execute: bool = False
) -> Generator[list[Callable[[], None]], None, None]:
    callbacks: list[Callable[[], None]] = []
    start_count = len(connections[using].run_on_commit)
    try:
        yield callbacks
    finally:
        while True:
            callback_count = len(connections[using].run_on_commit)
            for _, callback in connections[using].run_on_commit[start_count:]:
                callbacks.append(callback)
                if execute:
                    callback()

            if callback_count == len(connections[using].run_on_commit):
                break
            start_count = callback_count


@pytest.fixture
def poland() -> Country:
    return Country.objects.create(name="Poland", iso_code2="PL", iso_code3="POL", iso_num="616")


@pytest.fixture
def germany() -> Country:
    return Country.objects.create(name="Germany", iso_code2="DE", iso_code3="DEU", iso_num="276")


@pytest.fixture
def program(poland: Country, germany: Country) -> Program:
    business_area = create_afghanistan()
    business_area.countries.add(poland, germany)

    return ProgramFactory(name="Test Program for Household", status=Program.ACTIVE, business_area=business_area)


@pytest.fixture
def admin1(state: AreaType) -> Area:
    return Area.objects.create(name="Kabul", area_type=state, p_code="AF11")


@pytest.fixture
def admin2(district: AreaType) -> Area:
    return Area.objects.create(name="Kabul1", area_type=district, p_code="AF1115")


@pytest.fixture
def state(poland: Country) -> AreaType:
    return AreaType.objects.create(name="State", country=poland)


@pytest.fixture
def district(poland: Country, state: AreaType) -> AreaType:
    return AreaType.objects.create(name="District", parent=state, country=poland)


@pytest.fixture
def merged_rdi(program: Program) -> RegistrationDataImport:
    return RegistrationDataImportFactory(program=program, status=RegistrationDataImport.MERGED)


@pytest.fixture
def in_review_rdi(program: Program) -> RegistrationDataImport:
    return RegistrationDataImportFactory(program=program, status=RegistrationDataImport.IN_REVIEW)


@pytest.fixture
def pending_household(
    program: Program, admin1: Area, in_review_rdi: RegistrationDataImport
) -> tuple[Household, Individual]:
    household, individuals = create_household_and_individuals(
        household_data={
            "unicef_id": "HH-20-0000.0002",
            "rdi_merge_status": "PENDING",
            "business_area": program.business_area,
            "program": program,
            "admin1": admin1,
            "size": 954,
            "returnee": True,
            "identification_key": "SAME-KEY-001",
            "registration_data_import": in_review_rdi,
        },
        individuals_data=[
            {
                "unicef_id": "IND-00-0000.0011",
                "rdi_merge_status": "PENDING",
                "business_area": program.business_area,
                "sex": MALE,
                "phone_no": "+48555444333",
                "identification_key": "IND-KEY-002",
                "registration_data_import": in_review_rdi,
            },
        ],
    )

    ind = individuals[0]

    ind.flex_fields = {"muac": 0}
    ind.save()
    household.flex_fields = {"eggs": "SOURCE"}
    household.save()

    return (household, ind)


@pytest.fixture
def merged_household(
    program: Program, admin1: Area, merged_rdi: RegistrationDataImport
) -> tuple[Household, tuple[Individual, Individual]]:
    household, individuals = create_household_and_individuals(
        household_data={
            "unicef_id": "HH-20-0000.2002",
            "rdi_merge_status": "MERGED",
            "business_area": program.business_area,
            "program": program,
            "admin1": admin1,
            "size": 3,
            "returnee": False,
            "address": "Destination Address",
            "identification_key": "SAME-KEY-001",
            "registration_data_import": merged_rdi,
        },
        individuals_data=[
            {
                "unicef_id": "IND-00-0000.2001",
                "rdi_merge_status": "MERGED",
                "business_area": program.business_area,
                "sex": MALE,
                "phone_no": "+48111222333",
                "full_name": "Destination Individual",
                "given_name": "Destination",
                "family_name": "Individual",
                "identification_key": "IND-KEY-001",
                "registration_data_import": merged_rdi,
            },
            {
                "unicef_id": "IND-00-0000.00134",
                "rdi_merge_status": "MERGED",
                "business_area": program.business_area,
                "sex": MALE,
                "phone_no": "+48123123123",
                "identification_key": "IND-KEY-002",
                "registration_data_import": merged_rdi,
            },
        ],
    )

    ind1 = individuals[0]
    ind2 = individuals[1]

    ind1.flex_fields = {"muac": 10}
    ind1.save()
    household.flex_fields = {"eggs": "DESTINATION"}
    household.save()

    return (household, (ind1, ind2))


def test_merge_rdi_with_collision(
    program: Program,
    pending_household: tuple[Household, Individual],
    merged_household: tuple[Household, Individual],
    in_review_rdi: RegistrationDataImport,
) -> None:
    """
    1. Create RdiMergeTask
    2. Pending Household which is collided should be removed
    3. Pending Individual which is collided should be removed
    4. Merged household should be updated with the pending household data
    5. Merged individual should be updated with the pending individual data
    5. Merged household should have added in_review_rdi to extra_rdis m2m
    """
    from hope.apps.registration_datahub.tasks.rdi_merge import RdiMergeTask

    # Enable collision detection in the program
    program.collision_detection_enabled = True
    from hope.apps.program.collision_detectors import (
        IdentificationKeyCollisionDetector,
    )

    program.collision_detector = IdentificationKeyCollisionDetector
    program.save()

    # Get the initial state before merging
    pending_household_obj, pending_individual = pending_household
    merged_household_obj, (merged_individual_to_remove, merged_individual) = merged_household

    # Store original values for later comparison
    pending_household_id = pending_household_obj.id
    pending_individual_id = pending_individual.id
    original_merged_size = merged_household_obj.size
    original_merged_flex_fields = merged_household_obj.flex_fields.copy()

    # Verify that the identification keys match (precondition for collision)
    assert pending_household_obj.identification_key == merged_household_obj.identification_key

    # Execute the RdiMergeTask
    task = RdiMergeTask()
    task.execute(str(in_review_rdi.id))

    # Refresh objects from database
    in_review_rdi.refresh_from_db()
    merged_household_obj.refresh_from_db()
    merged_individual.refresh_from_db()

    # 1. Verify RDI status changed to MERGED
    assert in_review_rdi.status == RegistrationDataImport.MERGED

    # 2-3. Verify that pending household/individual were removed
    assert not Household.all_objects.filter(id=pending_household_id).exists()
    assert not Individual.all_objects.filter(id=pending_individual_id).exists()

    # 4. Verify merged household was updated with pending household data
    assert merged_household_obj.size == pending_household_obj.size
    assert merged_household_obj.returnee == pending_household_obj.returnee
    assert merged_household_obj.flex_fields.get("eggs") == pending_household_obj.flex_fields.get("eggs")
    assert merged_household_obj.size != original_merged_size
    assert merged_household_obj.flex_fields.get("eggs") != original_merged_flex_fields.get("eggs")

    # 5. Verify merged individual was updated with pending individual data
    individual_to_check = merged_household_obj.individuals.get(identification_key=pending_individual.identification_key)
    assert individual_to_check.flex_fields.get("muac") == pending_individual.flex_fields.get("muac")
    assert not Individual.all_objects.filter(id=merged_individual_to_remove.id).exists()
    # 6. Verify merged household has the in_review_rdi in extra_rdis
    assert in_review_rdi in merged_household_obj.extra_rdis.all()
