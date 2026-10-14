"""Tests for the CW-only ingest guard in BaseRegistrationService.create_rdi.

`_validate_business_area_can_create_rdi` rejects RDI creation for a
`COUNTRY_WORKSPACE_ONLY` business area before any RDI / ImportData row is
materialised, while leaving `ALL_EXCEPT_COUNTRY_WORKSPACE` business areas
untouched (regression). The concrete `GenericRegistrationService` is used to
exercise the abstract base.
"""

from django.core.exceptions import ValidationError
import pytest

from extras.test_utils.factories import (
    BusinessAreaFactory,
    DataCollectingTypeFactory,
    OrganizationFactory,
    ProgramFactory,
    ProjectFactory,
    RegistrationFactory,
    UserFactory,
)
from hope.contrib.aurora.models import Registration
from hope.contrib.aurora.services.generic_registration_service import GenericRegistrationService
from hope.models import BusinessArea, ImportData, RegistrationDataImport, User
from hope.models.business_area import ALL_EXCEPT_CW_INGEST_REJECT_MSG

pytestmark = pytest.mark.django_db


def _registration_for_ingest_source(ingest_source: str) -> Registration:
    business_area = BusinessAreaFactory(ingest_source=ingest_source)
    data_collecting_type = DataCollectingTypeFactory()
    data_collecting_type.limit_to.add(business_area)
    program = ProgramFactory(status="ACTIVE", data_collecting_type=data_collecting_type, business_area=business_area)
    organization = OrganizationFactory(business_area=business_area, slug=business_area.slug)
    project = ProjectFactory(organization=organization, programme=program)
    return RegistrationFactory(project=project)


@pytest.fixture
def cw_only_registration() -> Registration:
    return _registration_for_ingest_source(BusinessArea.IngestSource.COUNTRY_WORKSPACE_ONLY)


@pytest.fixture
def all_except_cw_registration() -> Registration:
    return _registration_for_ingest_source(BusinessArea.IngestSource.ALL_EXCEPT_COUNTRY_WORKSPACE)


@pytest.fixture
def user() -> User:
    return UserFactory.create()


def test_create_rdi_rejected_for_cw_only_business_area(cw_only_registration: Registration, user: User) -> None:
    service = GenericRegistrationService(cw_only_registration)

    with pytest.raises(ValidationError) as exc_info:
        service.create_rdi(imported_by=user, rdi_name="cw-only rdi")

    assert exc_info.value.messages == [ALL_EXCEPT_CW_INGEST_REJECT_MSG]


def test_create_rdi_creates_no_rows_for_cw_only_business_area(cw_only_registration: Registration, user: User) -> None:
    service = GenericRegistrationService(cw_only_registration)

    with pytest.raises(ValidationError):
        service.create_rdi(imported_by=user, rdi_name="cw-only rdi")

    assert RegistrationDataImport.objects.count() == 0
    assert ImportData.objects.count() == 0


def test_create_rdi_succeeds_for_all_except_cw_business_area(
    all_except_cw_registration: Registration, user: User
) -> None:
    service = GenericRegistrationService(all_except_cw_registration)

    rdi = service.create_rdi(imported_by=user, rdi_name="all-except rdi")

    assert rdi.pk is not None
    assert rdi.data_source == RegistrationDataImport.FLEX_REGISTRATION
    assert RegistrationDataImport.objects.filter(pk=rdi.pk).exists()
