import pytest

from extras.test_utils.factories import (
    HouseholdFactory,
    PendingHouseholdFactory,
    ProgramFactory,
    RegistrationDataImportFactory,
)
from hope.models import (
    BeneficiaryGroup,
    BusinessArea,
    DataCollectingType,
    Partner,
    Program,
    RegistrationDataImport,
    User,
)


@pytest.fixture
def rdi_business_area(business_area: BusinessArea) -> BusinessArea:
    # Without postponed deduplication the import needs Elasticsearch and ends in IMPORT_ERROR.
    business_area.postpone_deduplication = True
    business_area.save(update_fields=["postpone_deduplication"])
    # The XLSX import looks up the WFP partner for the scope_id columns.
    Partner.objects.get_or_create(name="WFP")
    return business_area


def _full_program(business_area: BusinessArea, name: str) -> Program:
    return ProgramFactory(
        name=name,
        status=Program.ACTIVE,
        business_area=business_area,
        data_collecting_type=DataCollectingType.objects.get(code="full"),
        beneficiary_group=BeneficiaryGroup.objects.get(name="Main Menu"),
    )


@pytest.fixture
def rdi_program(rdi_business_area: BusinessArea) -> Program:
    return _full_program(rdi_business_area, "RDI Target Programme")


@pytest.fixture
def source_program(rdi_business_area: BusinessArea) -> Program:
    program = _full_program(rdi_business_area, "RDI Source Programme")
    HouseholdFactory.create_batch(3, business_area=rdi_business_area, program=program)
    return program


def _rdi_with_pending_households(program: Program, status: str, imported_by: User) -> RegistrationDataImport:
    rdi = RegistrationDataImportFactory(
        business_area=program.business_area,
        program=program,
        status=status,
        imported_by=imported_by,
        number_of_households=2,
        number_of_individuals=2,
    )
    PendingHouseholdFactory.create_batch(
        2, business_area=program.business_area, program=program, registration_data_import=rdi
    )
    return rdi


@pytest.fixture
def in_review_rdi(rdi_program: Program, create_super_user: User) -> RegistrationDataImport:
    return _rdi_with_pending_households(rdi_program, RegistrationDataImport.IN_REVIEW, create_super_user)


@pytest.fixture
def import_error_rdi(rdi_program: Program, create_super_user: User) -> RegistrationDataImport:
    return _rdi_with_pending_households(rdi_program, RegistrationDataImport.IMPORT_ERROR, create_super_user)
