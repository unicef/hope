import pytest

from extras.test_utils.factories import (
    BusinessAreaFactory,
    DataCollectingTypeFactory,
    HouseholdFactory,
    IndividualFactory,
    ProgramFactory,
)
from hope.apps.household.forms import MassEnrollForm
from hope.models import Household, Program

pytestmark = pytest.mark.django_db


@pytest.fixture
def business_area():
    return BusinessAreaFactory(slug="afghanistan", name="Afghanistan")


@pytest.fixture
def data_collecting_type(business_area):
    dct = DataCollectingTypeFactory()
    dct.limit_to.add(business_area)
    return dct


@pytest.fixture
def program(business_area, data_collecting_type):
    return ProgramFactory(
        name="Test Program 333",
        business_area=business_area,
        status=Program.ACTIVE,
        data_collecting_type=data_collecting_type,
    )


@pytest.fixture
def household(program):
    return HouseholdFactory(
        program=program,
        business_area=program.business_area,
        head_of_household=IndividualFactory(household=None),
    )


def test_clean_form(business_area, program, household) -> None:
    form_data = {"program_for_enroll": program.id, "apply": True}
    form = MassEnrollForm(
        data=form_data,
        business_area_id=str(business_area.id),
        households=Household.objects.filter(id=household.id),
    )
    assert form.is_valid()
