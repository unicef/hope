import pytest

from extras.test_utils.factories import (
    AccountTypeFactory,
    AreaFactory,
    AreaTypeFactory,
    BusinessAreaFactory,
    CountryFactory,
    DataCollectingTypeFactory,
    DocumentTypeFactory,
    FinancialInstitutionFactory,
    ProgramFactory,
)
from hope.models import (
    BeneficiaryGroup,
    BusinessArea,
    DataCollectingType,
    FinancialInstitution,
    Program,
)

SOMALIA_PROGRAM_NAME = "Somalia Test Program"


@pytest.fixture
def somalia_business_area(business_area: BusinessArea) -> BusinessArea:
    country = CountryFactory(name="Somalia", iso_code2="SO", iso_code3="SOM", iso_num="706")
    somalia = BusinessAreaFactory(
        code="0620",
        name="Somalia",
        long_name="THE FEDERAL REPUBLIC OF SOMALIA",
        region_code="62",
        region_name="ESARO",
        slug="somalia",
        has_data_sharing_agreement=True,
        is_accountability_applicable=True,
        timezone="UTC",
    )
    somalia.countries.add(country)
    # XlsxSomaliaParser looks up the admin area and the lookups below by these exact names and keys.
    region = AreaTypeFactory(name="Region", area_level=1, country=country)
    AreaFactory(name="JALALAQSI", p_code="SO2105", area_type=region)
    FinancialInstitutionFactory(
        name="Hormuud Telecom", type=FinancialInstitution.FinancialInstitutionType.TELCO, country=country
    )
    FinancialInstitutionFactory(name="Generic Bank", type=FinancialInstitution.FinancialInstitutionType.BANK)
    FinancialInstitutionFactory(name="Generic Telco Company", type=FinancialInstitution.FinancialInstitutionType.TELCO)
    DocumentTypeFactory(key="passport", label="Passport", is_identity_document=True)
    AccountTypeFactory(key="mobile", label="Mobile Money", unique_fields=["number"])
    return somalia


@pytest.fixture
def somalia_program(somalia_business_area: BusinessArea) -> Program:
    dct = DataCollectingTypeFactory(type=DataCollectingType.Type.STANDARD)
    dct.limit_to.add(somalia_business_area)
    return ProgramFactory(
        name=SOMALIA_PROGRAM_NAME,
        status=Program.ACTIVE,
        business_area=somalia_business_area,
        data_collecting_type=dct,
        beneficiary_group=BeneficiaryGroup.objects.get(name="Main Menu"),
    )
