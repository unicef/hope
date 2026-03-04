import datetime

import pytest

from extras.test_utils.factories import (
    AreaFactory,
    AreaTypeFactory,
    BusinessAreaFactory,
    CountryFactory,
    HouseholdFactory,
    IndividualFactory,
    PendingHouseholdFactory,
    PendingIndividualFactory,
    ProgramFactory,
    RegistrationDataImportFactory,
)
from hope.apps.household.const import MALE, REMOVED_BY_COLLISION
from hope.models import Household, Individual, Program, RegistrationDataImport
from hope.models.utils import MergeStatusModel

pytestmark = [
    pytest.mark.usefixtures("django_elasticsearch_setup"),
    pytest.mark.elasticsearch,
    pytest.mark.django_db,
]


@pytest.fixture
def poland() -> object:
    return CountryFactory(name="Poland", iso_code2="PL", iso_code3="POL", iso_num="616")


@pytest.fixture
def germany() -> object:
    return CountryFactory(name="Germany", iso_code2="DE", iso_code3="DEU", iso_num="276")


@pytest.fixture
def business_area(poland: object, germany: object) -> object:
    business_area = BusinessAreaFactory(slug="afghanistan", name="Afghanistan")
    business_area.countries.add(poland, germany)
    return business_area


@pytest.fixture
def program(business_area: object) -> Program:
    return ProgramFactory(
        name="Test Program for Household",
        status=Program.ACTIVE,
        business_area=business_area,
    )


@pytest.fixture
def state(poland: object) -> object:
    return AreaTypeFactory(name="State", area_level=1, country=poland)


@pytest.fixture
def admin1(state: object) -> object:
    return AreaFactory(name="Kabul", area_type=state, p_code="AF11")


@pytest.fixture
def merged_rdi(program: Program) -> RegistrationDataImport:
    return RegistrationDataImportFactory(program=program, status=RegistrationDataImport.MERGED)


@pytest.fixture
def in_review_rdi(program: Program) -> RegistrationDataImport:
    return RegistrationDataImportFactory(program=program, status=RegistrationDataImport.IN_REVIEW)


@pytest.fixture
def pending_household(
    program: Program, admin1: object, in_review_rdi: RegistrationDataImport
) -> tuple[Household, Individual]:
    pending_individual = PendingIndividualFactory(
        unicef_id="IND-00-0000.0011",
        rdi_merge_status=MergeStatusModel.PENDING,
        business_area=program.business_area,
        program=program,
        sex=MALE,
        phone_no="+48555444333",
        identification_key="IND-KEY-002",
        registration_data_import=in_review_rdi,
        household=None,
        birth_date=datetime.date(2000, 1, 1),
    )
    household = PendingHouseholdFactory(
        unicef_id="HH-20-0000.0002",
        rdi_merge_status=MergeStatusModel.PENDING,
        business_area=program.business_area,
        program=program,
        admin1=admin1,
        size=954,
        returnee=True,
        identification_key="SAME-KEY-001",
        registration_data_import=in_review_rdi,
        head_of_household=pending_individual,
        create_role=False,
    )

    pending_individual.flex_fields = {"muac": 0}
    pending_individual.household = household
    pending_individual.save(update_fields=["flex_fields", "household"])
    household.flex_fields = {"eggs": "SOURCE"}
    household.save(update_fields=["flex_fields"])

    return (household, pending_individual)


@pytest.fixture
def merged_household(
    program: Program, admin1: object, merged_rdi: RegistrationDataImport
) -> tuple[Household, tuple[Individual, Individual]]:
    ind1 = IndividualFactory(
        unicef_id="IND-00-0000.2001",
        rdi_merge_status=MergeStatusModel.MERGED,
        business_area=program.business_area,
        program=program,
        sex=MALE,
        phone_no="+48111222333",
        full_name="Destination Individual",
        given_name="Destination",
        family_name="Individual",
        identification_key="IND-KEY-001",
        registration_data_import=merged_rdi,
        household=None,
        birth_date=datetime.date(1990, 1, 1),
    )
    ind2 = IndividualFactory(
        unicef_id="IND-00-0000.00134",
        rdi_merge_status=MergeStatusModel.MERGED,
        business_area=program.business_area,
        program=program,
        sex=MALE,
        phone_no="+48123123123",
        identification_key="IND-KEY-002",
        registration_data_import=merged_rdi,
        household=None,
        birth_date=datetime.date(1995, 1, 1),
    )
    household = HouseholdFactory(
        unicef_id="HH-20-0000.2002",
        rdi_merge_status=MergeStatusModel.MERGED,
        business_area=program.business_area,
        program=program,
        admin1=admin1,
        size=3,
        returnee=False,
        address="Destination Address",
        identification_key="SAME-KEY-001",
        registration_data_import=merged_rdi,
        head_of_household=ind1,
        create_role=False,
    )
    ind2.household = household
    ind2.save(update_fields=["household"])

    ind1.flex_fields = {"muac": 10}
    ind1.save(update_fields=["flex_fields"])
    household.flex_fields = {"eggs": "DESTINATION"}
    household.save(update_fields=["flex_fields"])

    return (household, (ind1, ind2))


def test_merge_rdi_with_collision(
    program: Program,
    pending_household: tuple[Household, Individual],
    merged_household: tuple[Household, tuple[Individual, Individual]],
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
    from hope.apps.program.collision_detectors import IdentificationKeyCollisionDetector
    from hope.apps.registration_data.tasks.rdi_merge import RdiMergeTask

    program.collision_detector = IdentificationKeyCollisionDetector
    program.save(update_fields=["collision_detector"])

    pending_household_obj, pending_individual = pending_household
    merged_household_obj, (merged_individual_to_remove, merged_individual) = merged_household

    pending_household_id = pending_household_obj.id
    pending_individual_id = pending_individual.id
    original_merged_size = merged_household_obj.size
    original_merged_flex_fields = merged_household_obj.flex_fields.copy()

    assert pending_household_obj.identification_key == merged_household_obj.identification_key

    task = RdiMergeTask()
    task.execute(str(in_review_rdi.id))

    in_review_rdi.refresh_from_db()
    merged_household_obj.refresh_from_db()
    merged_individual.refresh_from_db()

    assert in_review_rdi.status == RegistrationDataImport.MERGED

    assert not Household.all_objects.filter(id=pending_household_id).exists()
    assert not Individual.all_objects.filter(id=pending_individual_id).exists()

    assert merged_household_obj.size == pending_household_obj.size
    assert merged_household_obj.returnee == pending_household_obj.returnee
    assert merged_household_obj.flex_fields.get("eggs") == pending_household_obj.flex_fields.get("eggs")
    assert merged_household_obj.size != original_merged_size
    assert merged_household_obj.flex_fields.get("eggs") != original_merged_flex_fields.get("eggs")

    individual_to_check = merged_household_obj.individuals.get(identification_key=pending_individual.identification_key)
    assert individual_to_check.flex_fields.get("muac") == pending_individual.flex_fields.get("muac")

    merged_individual_to_remove.refresh_from_db()
    assert Individual.all_objects.filter(id=merged_individual_to_remove.id).exists()
    assert merged_individual_to_remove.withdrawn is True
    assert merged_individual_to_remove.relationship == REMOVED_BY_COLLISION
    assert "removed_by_collision_detector" in merged_individual_to_remove.internal_data

    assert in_review_rdi in merged_household_obj.extra_rdis.all()
