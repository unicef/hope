import pytest

from extras.test_utils.factories import (
    BusinessAreaFactory,
    PendingHouseholdFactory,
    ProgramFactory,
    RegistrationDataImportFactory,
)
from hope.api.endpoints.rdi.mixin import HouseholdUploadMixin
from hope.models import HEAD, RegistrationDataImport

pytestmark = pytest.mark.django_db


@pytest.fixture
def business_area():
    return BusinessAreaFactory()


@pytest.fixture
def program(business_area):
    return ProgramFactory(business_area=business_area)


@pytest.fixture
def rdi_without_program(business_area, program):
    rdi = RegistrationDataImportFactory(business_area=business_area, program=program)
    RegistrationDataImport.objects.filter(pk=rdi.pk).update(program=None)
    rdi.refresh_from_db()
    return rdi


def test_save_member_raises_when_rdi_has_no_program(business_area, program, rdi_without_program):
    hh = PendingHouseholdFactory(
        registration_data_import=rdi_without_program,
        business_area=business_area,
        program=program,
    )
    member_data = {
        "relationship": HEAD,
        "full_name": "Test Person",
        "given_name": "Test",
        "family_name": "Person",
        "birth_date": "2000-01-01",
        "sex": "MALE",
    }
    mixin = HouseholdUploadMixin()

    with pytest.raises(ValueError, match="RDI program must not be None"):
        mixin.save_member(rdi_without_program, hh, member_data)
