import pytest

from extras.test_utils.factories import DataCollectingTypeFactory, ProgramFactory
from hope.models import (
    AccountType,
    Area,
    AreaType,
    BeneficiaryGroup,
    BusinessArea,
    Country,
    DataCollectingType,
    DocumentType,
    FinancialInstitution,
    Program,
)

SOMALIA_PROGRAM_NAME = "Somalia Test Program"


@pytest.fixture
def somalia_business_area(business_area: BusinessArea) -> BusinessArea:
    somalia, _ = BusinessArea.objects.get_or_create(
        code="0620",
        defaults={
            "name": "Somalia",
            "long_name": "THE FEDERAL REPUBLIC OF SOMALIA",
            "region_code": "62",
            "region_name": "ESARO",
            "slug": "somalia",
            "has_data_sharing_agreement": True,
            "is_accountability_applicable": True,
            "active": True,
            "timezone": "UTC",
        },
    )
    country, _ = Country.objects.get_or_create(
        iso_code3="SOM", defaults={"name": "Somalia", "iso_code2": "SO", "iso_num": "706"}
    )
    somalia.countries.add(country)
    # XlsxSomaliaParser looks up the admin area and the lookups below by these exact names and keys.
    region, _ = AreaType.objects.get_or_create(name="Region", area_level=1, country=country)
    Area.objects.get_or_create(name="JALALAQSI", p_code="SO2105", area_type=region)
    FinancialInstitution.objects.get_or_create(
        name="Hormuud Telecom",
        defaults={"type": FinancialInstitution.FinancialInstitutionType.TELCO, "country": country},
    )
    FinancialInstitution.objects.get_or_create(
        name="Generic Bank", defaults={"type": FinancialInstitution.FinancialInstitutionType.BANK}
    )
    FinancialInstitution.objects.get_or_create(
        name="Generic Telco Company", defaults={"type": FinancialInstitution.FinancialInstitutionType.TELCO}
    )
    DocumentType.objects.get_or_create(key="passport", defaults={"label": "Passport", "is_identity_document": True})
    AccountType.objects.get_or_create(key="mobile", defaults={"label": "Mobile Money", "unique_fields": ["number"]})
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
