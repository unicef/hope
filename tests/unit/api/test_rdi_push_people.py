import pytest

from extras.test_utils.factories import (
    BusinessAreaFactory,
    PendingHouseholdFactory,
    ProgramFactory,
    RegistrationDataImportFactory,
)
from hope.api.endpoints.rdi.push_people import PeopleUploadMixin
from hope.models import RegistrationDataImport

pytestmark = pytest.mark.django_db


@pytest.fixture
def business_area():
    return BusinessAreaFactory()


@pytest.fixture
def program(business_area):
    return ProgramFactory(business_area=business_area)


@pytest.fixture
def rdi_with_program(business_area, program):
    return RegistrationDataImportFactory(business_area=business_area, program=program)


@pytest.fixture
def rdi_without_program(business_area, program):
    rdi = RegistrationDataImportFactory(business_area=business_area, program=program)
    RegistrationDataImport.objects.filter(pk=rdi.pk).update(program=None)
    rdi.refresh_from_db()
    return rdi


def test_create_individual_raises_when_rdi_has_no_program(
    business_area, program, rdi_with_program, rdi_without_program
):
    hh = PendingHouseholdFactory(
        registration_data_import=rdi_without_program,
        business_area=business_area,
        program=program,
    )

    mixin = PeopleUploadMixin()
    # selected_rdi has a program (for photo path prefix), but the rdi argument has None
    mixin.selected_rdi = rdi_with_program

    with pytest.raises(ValueError, match="RDI program must not be None"):
        mixin._create_individual([], [], hh, {"photo": None}, rdi_without_program)
