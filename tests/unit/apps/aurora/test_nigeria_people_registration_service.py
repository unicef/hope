import datetime
import json

from django.utils import timezone
import pytest

from extras.test_utils.factories import (
    AccountTypeFactory,
    AreaFactory,
    AreaTypeFactory,
    BusinessAreaFactory,
    CountryFactory,
    DataCollectingTypeFactory,
    DeliveryMechanismFactory,
    DocumentTypeFactory,
    FinancialInstitutionFactory,
    FinancialServiceProviderFactory,
    OrganizationFactory,
    ProgramFactory,
    ProjectFactory,
    RecordFactory,
    RegistrationFactory,
    UserFactory,
)
from hope.apps.household.const import HEAD, MALE
from hope.contrib.aurora.services.nigeria_people_registration_service import NigeriaPeopleRegistrationService
from hope.models import (
    FinancialInstitutionMapping,
    PendingAccount,
    PendingDocument,
    PendingHousehold,
    PendingIndividual,
)

pytestmark = pytest.mark.django_db


@pytest.fixture
def nigeria_country() -> object:
    return CountryFactory(name="Nigeria", short_name="Nigeria", iso_code2="NG", iso_code3="NGA", iso_num="0566")


@pytest.fixture
def nigeria_admin_areas(nigeria_country: object) -> dict:
    area_type_1 = AreaTypeFactory(name="State", area_level=1, country=nigeria_country)
    area_type_2 = AreaTypeFactory(
        name="Local government area",
        area_level=2,
        country=nigeria_country,
        parent=area_type_1,
    )
    area_type_3 = AreaTypeFactory(name="Ward", area_level=3, country=nigeria_country, parent=area_type_2)
    area_1 = AreaFactory(name="Borno", p_code="NG002", area_type=area_type_1)
    area_2 = AreaFactory(name="Bama", p_code="NG002001", area_type=area_type_2, parent=area_1)
    area_3 = AreaFactory(name="Andara", p_code="NG002001007", area_type=area_type_3, parent=area_2)
    return {
        "area_type_1": area_type_1,
        "area_type_2": area_type_2,
        "area_type_3": area_type_3,
        "area_1": area_1,
        "area_2": area_2,
        "area_3": area_3,
    }


@pytest.fixture
def document_type() -> object:
    return DocumentTypeFactory(key="national_id", label="National ID")


@pytest.fixture
def business_area() -> object:
    return BusinessAreaFactory(slug="some-ng-slug")


@pytest.fixture
def data_collecting_type(business_area: object) -> object:
    data_collecting_type = DataCollectingTypeFactory(label="someLabel", code="some_label")
    data_collecting_type.limit_to.add(business_area)
    return data_collecting_type


@pytest.fixture
def program(business_area: object, data_collecting_type: object) -> object:
    return ProgramFactory(
        status="ACTIVE",
        data_collecting_type=data_collecting_type,
        biometric_deduplication_enabled=True,
        business_area=business_area,
    )


@pytest.fixture
def organization(business_area: object) -> object:
    return OrganizationFactory(business_area=business_area, slug=business_area.slug)


@pytest.fixture
def project(organization: object, program: object) -> object:
    return ProjectFactory(name="fake_project", organization=organization, programme=program)


@pytest.fixture
def registration(project: object) -> object:
    return RegistrationFactory(name="fake_registration", project=project, mapping={})


@pytest.fixture
def record_files() -> dict:
    return {
        "individual-details": [
            {
                "photo_i_c": "/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAP/////////////////////////////////////////////"
                "/////////////////////////////////////////wgALCAABAAEBAREA/8QAFBABAAAAAAAAAAAAA"
                "AAAAAAAAP/aAAgBAQABPxA=",
                "national_id_photo_i_c": "/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAP///////////////////////////////////"
                "///////////////////////////////////////////////////wgALCAABAAEBAREA/8QAF"
                "BABAAAAAAAAAAAAAAAAAAAAAP/aAAgBAQABPxA=",
            }
        ]
    }


@pytest.fixture
def record_fields() -> dict:
    return {
        "household-info": [{"admin1_h_c": "NG002", "admin2_h_c": "NG002001", "admin3_h_c": "NG002001007"}],
        "intro-and-consent": [{"consent_h_c": True, "enumerator_code": "SHEAbi5350", "who_to_register": "myself"}],
        "individual-details": [
            {
                "email_i_c": "gfranco@unicef.org",
                "gender_i_c": "male",
                "phone_no_i_c": "+2348023456789",
                "birth_date_i_c": "1988-04-08",
                "given_name_i_c": "Giulio",
                "middle_name_i_c": "D",
                "national_id_no": "01234567891",
                "account_details": {
                    "uba_code": "000004",
                    "name": "United Bank for Africa",
                    "number": "2087008012",
                    "holder_name": "xxxx",
                },
                "family_name_i_c": "Franco",
                "national_id_no_i_c": "01234567891",
                "estimated_birth_date_i_c": "y",
                "frontline_worker_designation_i_f": "H2HCL",
            }
        ],
    }


@pytest.fixture
def record(record_fields: dict, record_files: dict) -> object:
    return RecordFactory(
        registration=25,
        timestamp=timezone.make_aware(datetime.datetime(2023, 5, 1)),
        source_id=1,
        files=json.dumps(record_files).encode(),
        fields=record_fields,
    )


@pytest.fixture
def user() -> object:
    return UserFactory.create()


@pytest.fixture
def account_type() -> object:
    return AccountTypeFactory(key="bank", label="Bank", unique_fields=[])


@pytest.fixture
def financial_institutions() -> dict:
    return {
        "generic": FinancialInstitutionFactory(name="Generic Bank"),
        "nigeria": FinancialInstitutionFactory(name="Nigeria Bank"),
    }


@pytest.fixture
def financial_service_provider() -> object:
    delivery_mechanism = DeliveryMechanismFactory()
    return FinancialServiceProviderFactory(
        name="United Bank for Africa - Nigeria",
        delivery_mechanisms=[delivery_mechanism],
    )


@pytest.fixture
def financial_institution_mapping(
    financial_institutions: dict,
    financial_service_provider: object,
) -> object:
    return FinancialInstitutionMapping.objects.create(
        financial_service_provider=financial_service_provider,
        financial_institution=financial_institutions["nigeria"],
        code="000004",
    )


def test_import_data_to_datahub(
    nigeria_country: object,
    nigeria_admin_areas: dict,
    document_type: object,
    account_type: object,
    financial_institution_mapping: object,
    registration: object,
    user: object,
    record: object,
    financial_institutions: dict,
) -> None:
    assert nigeria_country
    assert nigeria_admin_areas
    assert document_type
    assert account_type
    assert financial_institution_mapping

    service = NigeriaPeopleRegistrationService(registration)
    rdi = service.create_rdi(user, f"nigeria rdi {datetime.datetime.now()}")
    service.process_records(rdi.id, [record.id])

    assert PendingHousehold.objects.count() == 1
    assert PendingHousehold.objects.filter(program=rdi.program).count() == 1

    household = PendingHousehold.objects.first()
    assert household
    assert household.consent
    assert household.country.iso_code2 == "NG"
    assert household.country_origin.iso_code2 == "NG"
    assert household.head_of_household == PendingIndividual.objects.get(given_name="Giulio")
    assert household.rdi_merge_status == "PENDING"
    assert household.flex_fields == {"enumerator_code": "SHEAbi5350", "who_to_register": "myself"}

    registration_data_import = household.registration_data_import
    assert registration_data_import.program == rdi.program

    primary_collector = PendingIndividual.objects.get(id=household.head_of_household_id)
    assert primary_collector.phone_no is not None
    assert primary_collector.sex == MALE
    assert primary_collector.email == "gfranco@unicef.org"
    assert primary_collector.full_name == "Giulio D Franco"
    assert primary_collector.relationship == HEAD
    assert primary_collector.phone_no_alternative is not None
    assert primary_collector.flex_fields == {
        "frontline_worker_designation_i_f": "H2HCL",
        "national_id_no": "01234567891",
    }
    assert primary_collector.rdi_merge_status == "PENDING"
    assert primary_collector.photo.url is not None

    account = PendingAccount.objects.first()
    assert account
    assert account.account_data == {
        "number": "2087008012",
        "name": "United Bank for Africa",
        "code": "000004",
        "holder_name": "xxxx",
        "financial_institution_pk": str(financial_institutions["nigeria"].id),
        "financial_institution_name": str(financial_institutions["nigeria"].name),
    }
    assert account.account_type.key == "bank"
    assert account.financial_institution == financial_institutions["nigeria"]

    national_id = PendingDocument.objects.filter(document_number="01234567891").first()
    assert national_id
    assert national_id.individual == primary_collector
    assert national_id.rdi_merge_status == "PENDING"
    assert national_id.photo.url is not None
