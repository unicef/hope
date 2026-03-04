import pytest

from extras.test_utils.factories import (
    BusinessAreaFactory,
    DataCollectingTypeFactory,
    HouseholdFactory,
    ProgramFactory,
    RegistrationDataImportFactory,
)
from hope.models import Household, Program

pytestmark = pytest.mark.django_db


@pytest.fixture
def business_area():
    return BusinessAreaFactory(slug="afghanistan", name="Afghanistan")


@pytest.fixture
def data_collecting_type():
    return DataCollectingTypeFactory(code="partial_individuals")


@pytest.fixture
def program(business_area, data_collecting_type):
    return ProgramFactory(
        name="Test program",
        business_area=business_area,
        status=Program.ACTIVE,
        data_collecting_type=data_collecting_type,
    )


@pytest.fixture
def registration_data_import(business_area, program):
    return RegistrationDataImportFactory(business_area=business_area, program=program)


def test_program_program_registration_id_trigger(registration_data_import, program, business_area) -> None:
    HouseholdFactory(
        registration_data_import=registration_data_import,
        program_registration_id="ABCD-123123",
        program=program,
        business_area=business_area,
    )
    HouseholdFactory(
        registration_data_import=registration_data_import,
        program_registration_id="ABCD-123123",
        program=program,
        business_area=business_area,
    )
    HouseholdFactory(
        registration_data_import=registration_data_import,
        program_registration_id="ABCD-123123",
        program=program,
        business_area=business_area,
    )
    HouseholdFactory(
        registration_data_import=registration_data_import,
        program_registration_id="ABCD-111222",
        program=program,
        business_area=business_area,
    )
    registrations_ids = list(
        Household.objects.filter(registration_data_import=registration_data_import)
        .order_by("program_registration_id")
        .values_list("program_registration_id", flat=True)
    )
    expected_program_registrations_ids = [
        "ABCD-111222#0",
        "ABCD-123123#0",
        "ABCD-123123#1",
        "ABCD-123123#2",
    ]
    assert registrations_ids == expected_program_registrations_ids
