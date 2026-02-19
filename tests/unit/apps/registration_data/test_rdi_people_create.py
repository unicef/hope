from datetime import date
from io import BytesIO
from pathlib import Path

from django.core.files import File
from django.forms import model_to_dict
from django_countries.fields import Country
import pytest

from extras.test_utils.factories.account import PartnerFactory
from extras.test_utils.factories.core import (
    BusinessAreaFactory,
    FlexibleAttributeFactory,
    FlexibleAttributeForPDUFactory,
)
from extras.test_utils.factories.geo import AreaFactory, AreaTypeFactory, CountryFactory
from extras.test_utils.factories.household import DocumentTypeFactory
from extras.test_utils.factories.payment import AccountTypeFactory, FinancialInstitutionFactory
from extras.test_utils.factories.program import ProgramFactory
from extras.test_utils.factories.registration_data import ImportDataFactory, RegistrationDataImportFactory
from hope.apps.household.const import ROLE_ALTERNATE, ROLE_PRIMARY
from hope.apps.registration_data.tasks.rdi_xlsx_people_create import RdiXlsxPeopleCreateTask
from hope.models import (
    Country as GeoCountry,
    DataCollectingType,
    FlexibleAttribute,
    PendingAccount,
    PendingHousehold,
    PendingIndividual,
    PeriodicFieldData,
    Program,
)
from hope.models.utils import MergeStatusModel

pytestmark = [pytest.mark.django_db, pytest.mark.usefixtures("mock_elasticsearch")]

FILES_DIR = Path(__file__).resolve().parent / "test_file"


DOCUMENT_TYPE_KEYS = [
    "birth_certificate",
    "tax_id",
    "drivers_license",
    "electoral_card",
    "national_passport",
    "national_id",
]


@pytest.fixture
def countries() -> dict[str, object]:
    afghanistan = CountryFactory(
        name="Afghanistan",
        short_name="Afghanistan",
        iso_code2="AF",
        iso_code3="AFG",
        iso_num="0004",
    )
    san_marino = CountryFactory(
        name="San Marino",
        short_name="San Marino",
        iso_code2="SM",
        iso_code3="SMR",
        iso_num="0674",
    )
    isle_of_man = CountryFactory(
        name="Isle of Man",
        short_name="Isle of Man",
        iso_code2="IM",
        iso_code3="IMN",
        iso_num="0833",
    )
    poland = CountryFactory(
        name="Poland",
        short_name="Poland",
        iso_code2="PL",
        iso_code3="POL",
        iso_num="0616",
    )
    saint_vincent = CountryFactory(
        name="Saint Vincent",
        short_name="Saint Vincent",
        iso_code2="VC",
        iso_code3="VCT",
        iso_num="0670",
    )
    return {
        "afghanistan": afghanistan,
        "san_marino": san_marino,
        "isle_of_man": isle_of_man,
        "poland": poland,
        "saint_vincent": saint_vincent,
    }


@pytest.fixture
def business_area(countries: dict[str, object]):
    business_area = BusinessAreaFactory(
        slug="afghanistan",
        name="Afghanistan",
        long_name="Afghanistan",
        active=True,
        postpone_deduplication=True,
        office_country=countries["afghanistan"],
    )
    business_area.countries.add(countries["afghanistan"])
    business_area.payment_countries.add(countries["afghanistan"])
    return business_area


@pytest.fixture
def admin_areas(countries: dict[str, object]) -> dict[str, object]:
    area_type_l1 = AreaTypeFactory(country=countries["afghanistan"], area_level=1)
    area_type_l2 = AreaTypeFactory(country=countries["afghanistan"], area_level=2, parent=area_type_l1)
    parent = AreaFactory(p_code="AF11", name="Name", area_type=area_type_l1)
    child = AreaFactory(p_code="AF1115", name="Name2", parent=parent, area_type=area_type_l2)
    return {"admin1": parent, "admin2": child}


@pytest.fixture
def partners() -> dict[str, object]:
    return {
        "unhcr": PartnerFactory(name="UNHCR"),
        "wfp": PartnerFactory(name="WFP"),
    }


@pytest.fixture
def document_types() -> list[object]:
    return [DocumentTypeFactory(key=key) for key in DOCUMENT_TYPE_KEYS]


@pytest.fixture
def account_type() -> object:
    return AccountTypeFactory(key="bank")


@pytest.fixture
def financial_institution() -> object:
    return FinancialInstitutionFactory(name="Generic Bank")


@pytest.fixture
def program(business_area) -> Program:
    return ProgramFactory(
        business_area=business_area,
        status=Program.ACTIVE,
        data_collecting_type__type=DataCollectingType.Type.SOCIAL,
        beneficiary_group__master_detail=False,
    )


@pytest.fixture
def pdu_attribute(program):
    return FlexibleAttributeForPDUFactory(
        label="PDU String Attribute",
        pdu_data__subtype=PeriodicFieldData.STRING,
        pdu_data__number_of_rounds=1,
        pdu_data__rounds_names=["May"],
        program=program,
    )


@pytest.fixture
def custom_attribute() -> object:
    return FlexibleAttributeFactory(
        name="custom_field_i_f",
        label={"English(EN)": "Custom Field"},
        type=FlexibleAttribute.DECIMAL,
        associated_with=FlexibleAttribute.ASSOCIATED_WITH_INDIVIDUAL,
        is_removed=False,
    )


@pytest.fixture
def import_data(business_area) -> object:
    content = (FILES_DIR / "rdi_people_test.xlsx").read_bytes()
    file = File(BytesIO(content), name="rdi_people_test.xlsx")
    return ImportDataFactory(
        file=file,
        number_of_households=0,
        number_of_individuals=4,
        business_area_slug=business_area.slug,
    )


@pytest.fixture
def registration_data_import(business_area, program, import_data) -> object:
    return RegistrationDataImportFactory(
        business_area=business_area,
        program=program,
        import_data=import_data,
        number_of_individuals=4,
        number_of_households=0,
    )


@pytest.fixture
def rdi_people_dependencies(
    admin_areas: dict[str, object],
    partners: dict[str, object],
    document_types: list[object],
    account_type: object,
    financial_institution: object,
    pdu_attribute: object,
    custom_attribute: object,
) -> dict[str, object]:
    return {
        "admin_areas": admin_areas,
        "partners": partners,
        "document_types": document_types,
        "account_type": account_type,
        "financial_institution": financial_institution,
        "pdu_attribute": pdu_attribute,
        "custom_attribute": custom_attribute,
    }


def test_execute(
    rdi_people_dependencies: dict[str, object],
    registration_data_import: object,
    import_data: object,
    business_area: object,
    program: Program,
) -> None:
    assert rdi_people_dependencies
    RdiXlsxPeopleCreateTask().execute(
        registration_data_import.id,
        import_data.id,
        business_area.id,
        program.id,
    )
    assert PendingHousehold.objects.count() == 5
    assert PendingIndividual.objects.count() == 5

    individual_data = {
        "full_name": "Derek Index4",
        "given_name": "Derek",
        "middle_name": "",
        "family_name": "Index4",
        "sex": "MALE",
        "relationship": "HEAD",
        "birth_date": date(2000, 8, 22),
        "marital_status": "MARRIED",
    }
    matching_individuals = PendingIndividual.objects.filter(**individual_data)

    assert matching_individuals.count() == 1
    individual = matching_individuals.first()
    assert individual.flex_fields == {
        "pdu_string_attribute": {"1": {"value": "Test PDU Value", "collection_date": "2020-01-08"}}
    }
    household_data = {
        "residence_status": "REFUGEE",
        "country": GeoCountry.objects.get(iso_code2=Country("IM").code).id,
        "zip_code": "002",
        "flex_fields": {},
    }
    household = individual.pending_household
    household_obj_data = model_to_dict(household, ("residence_status", "country", "zip_code", "flex_fields"))
    assert household_obj_data == household_data

    roles = household.individuals_and_roles(manager="pending_objects").all()
    assert roles.count() == 2
    primary_role = roles.get(role=ROLE_PRIMARY)
    assert primary_role.role == ROLE_PRIMARY
    assert primary_role.individual.full_name == "Derek Index4"
    alternate_role = roles.get(role=ROLE_ALTERNATE)
    assert alternate_role.role == ROLE_ALTERNATE
    assert alternate_role.individual.full_name == "Collector ForJanIndex_3"
    assert alternate_role.individual.flex_fields["custom_field_i_f"] == 2.99

    worker_individuals = PendingIndividual.objects.filter(relationship="NON_BENEFICIARY")
    assert worker_individuals.count() == 2

    assert PendingAccount.objects.count() == 3
    dmd1 = PendingAccount.objects.get(individual__full_name="Collector ForJanIndex_3")
    dmd2 = PendingAccount.objects.get(individual__full_name="WorkerCollector ForDerekIndex_4")
    dmd3 = PendingAccount.objects.get(individual__full_name="Jan    Index3")
    assert dmd1.rdi_merge_status == MergeStatusModel.PENDING
    assert dmd2.rdi_merge_status == MergeStatusModel.PENDING
    assert dmd3.rdi_merge_status == MergeStatusModel.PENDING
    assert dmd1.data == {
        "card_number": "164260858",
        "card_expiry_date": "1995-06-03T00:00:00",
    }
    assert dmd2.data == {
        "card_number": "1975549730",
        "card_expiry_date": "2022-02-17T00:00:00",
        "name_of_cardholder": "Name1",
    }
    assert dmd3.data == {
        "card_number": "870567340",
        "card_expiry_date": "2016-06-27T00:00:00",
        "name_of_cardholder": "Name2",
    }
