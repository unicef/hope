import copy
import datetime
import json

from django.utils import timezone
import pytest

from extras.test_utils.factories import (
    AreaFactory,
    AreaTypeFactory,
    BusinessAreaFactory,
    CountryFactory,
    DataCollectingTypeFactory,
    DocumentTypeFactory,
    OrganizationFactory,
    ProgramFactory,
    ProjectFactory,
    RecordFactory,
    RegistrationFactory,
    UserFactory,
)
from hope.apps.core.utils import IDENTIFICATION_TYPE_TO_KEY_MAPPING
from hope.apps.household.const import IDENTIFICATION_TYPE_TAX_ID, ROLE_ALTERNATE, ROLE_PRIMARY
from hope.contrib.aurora.models import Record
from hope.contrib.aurora.services.generic_registration_service import GenericRegistrationService
from hope.models import (
    PendingDocument,
    PendingHousehold,
    PendingIndividual,
    PendingIndividualRoleInHousehold,
)

pytestmark = pytest.mark.django_db


@pytest.fixture
def ukraine_country() -> object:
    return CountryFactory(name="Ukraine", short_name="Ukraine", iso_code2="UA", iso_code3="UKR", iso_num="0804")


@pytest.fixture
def ukraine_admin_areas(ukraine_country: object) -> dict:
    admin1_type = AreaTypeFactory(name="Admin1", country=ukraine_country, area_level=1)
    admin2_type = AreaTypeFactory(name="Admin2", country=ukraine_country, area_level=2, parent=admin1_type)
    admin3_type = AreaTypeFactory(name="Admin3", country=ukraine_country, area_level=3, parent=admin2_type)
    admin1 = AreaFactory(p_code="UA07", name="Name1", area_type=admin1_type)
    admin2 = AreaFactory(p_code="UA0702", name="Name2", parent=admin1, area_type=admin2_type)
    admin3 = AreaFactory(p_code="UA0114007", name="Name3", parent=admin2, area_type=admin3_type)
    return {
        "admin1_type": admin1_type,
        "admin2_type": admin2_type,
        "admin3_type": admin3_type,
        "admin1": admin1,
        "admin2": admin2,
        "admin3": admin3,
    }


@pytest.fixture
def document_types() -> dict:
    tax_id = DocumentTypeFactory(key="tax_id", label="Tax ID")
    disability = DocumentTypeFactory(key="disability_certificate", label="Disability Certificate")
    return {"tax_id": tax_id, "disability_certificate": disability}


@pytest.fixture
def business_area() -> object:
    return BusinessAreaFactory(slug="generic-slug")


@pytest.fixture
def data_collecting_type(business_area: object) -> object:
    data_collecting_type = DataCollectingTypeFactory(label="SomeFull", code="some_full")
    data_collecting_type.limit_to.add(business_area)
    return data_collecting_type


@pytest.fixture
def program(business_area: object, data_collecting_type: object) -> object:
    return ProgramFactory(status="ACTIVE", data_collecting_type=data_collecting_type, business_area=business_area)


@pytest.fixture
def organization(business_area: object) -> object:
    return OrganizationFactory(business_area=business_area, slug=business_area.slug)


@pytest.fixture
def project(organization: object, program: object) -> object:
    return ProjectFactory(name="fake_project", organization=organization, programme=program)


@pytest.fixture
def registration_mapping() -> dict:
    return {
        "defaults": {"business_area": "ukraine", "country": "UA"},
        "household": {
            "admin1_h_c": "household.admin1",
            "admin2_h_c": "household.admin2",
            "admin3_h_c": "household.admin3",
            "admin4_h_c": "household.admin4",
            "ff": "household.flex_fields",
        },
        "individuals": {
            "birth_date": "individual.birth_date",
            "patronymic": "individual.middle_name",
            "id_type": "document.doc_tax-key",
            "disability_id_type_i_c": "document.disability_certificate-key",
            "disability_id_i_c": "document.disability_certificate-document_number",
            "disability_id_photo_i_c": "document.disability_certificate-photo",
        },
        "flex_fields": [
            "marketing.can_unicef_contact_you",
            "enumerators",
            "macioce",
        ],
        "household_constances": {"zip_code": "00126"},
        "individual_constances": {"pregnant": True},
    }


@pytest.fixture
def registration(project: object, registration_mapping: dict) -> object:
    return RegistrationFactory(name="fake_registration", project=project, mapping=registration_mapping)


@pytest.fixture
def user() -> object:
    return UserFactory.create()


@pytest.fixture
def record_defaults() -> dict:
    return {
        "registration": 2,
        "timestamp": timezone.make_aware(datetime.datetime(2022, 4, 1)),
    }


@pytest.fixture
def base_household() -> list[dict]:
    return [
        {
            "residence_status_h_c": "NON_HOST",
            "where_are_you_now": "",
            "admin1_h_c": "UA07",
            "admin2_h_c": "UA0702",
            "admin3_h_c": "UA0114007",
            "size_h_c": 5,
            "ff": "random",
        }
    ]


@pytest.fixture
def individual_with_bank_account_and_tax_and_disability() -> dict:
    return {
        "id_type": "tax_id",
        "tax_id_no_i_c": "123123123",
        "bank_account_h_f": "y",
        "relationship_i_c": "head",
        "given_name_i_c": "Jan",
        "family_name_i_c": "Romaniak",
        "patronymic": "Roman",
        "birth_date": "1991-11-18",
        "gender_i_c": "male",
        "phone_no_i_c": "+393892781511",
        "email": "email123@mail.com",
        "role_pr_i_c": "y",
        "disability_id_type_i_c": "disability_certificate",
        "disability_id_i_c": "xyz",
    }


@pytest.fixture
def individual_with_bank_account_and_tax() -> dict:
    return {
        "id_type": "tax_id",
        "tax_id_no_i_c": "123123123",
        "bank_account_h_f": "y",
        "relationship_i_c": "head",
        "given_name_i_c": "Wiktor",
        "family_name_i_c": "Lamiący",
        "patronymic": "Stefan",
        "birth_date": "1991-11-18",
        "gender_i_c": "male",
        "phone_no_i_c": "+393451232123",
        "email": "email321@mail.com",
    }


@pytest.fixture
def individual_with_no_tax() -> dict:
    return {
        "tax_id_no_i_c": "",
        "bank_account_h_f": "y",
        "relationship_i_c": "head",
        "given_name_i_c": "Michał",
        "family_name_i_c": "Brzęczący",
        "patronymic": "Janusz",
        "birth_date": "1991-11-18",
        "gender_i_c": "male",
        "phone_no_i_c": "+393451232124",
        "email": "email111@mail.com",
        "role_sec_i_c": "y",
    }


@pytest.fixture
def individual_without_bank_account() -> dict:
    return {
        "id_type": "tax_id",
        "tax_id_no_i_c": "TESTID",
        "bank_account_h_f": "",
        "relationship_i_c": "head",
        "given_name_i_c": "Aleksiej",
        "family_name_i_c": "Prysznicow",
        "patronymic": "Paweł",
        "birth_date": "1991-11-18",
        "gender_i_c": "male",
        "phone_no_i_c": "+393451212123",
        "email": "email222@mail.com",
    }


@pytest.fixture
def individual_with_tax_id_which_is_too_long() -> dict:
    return {
        "id_type": "tax_id",
        "tax_id_no_i_c": "x" * 300,
        "bank_account_h_f": "",
        "relationship_i_c": "head",
        "given_name_i_c": "Aleksiej",
        "family_name_i_c": "Prysznicow",
        "patronymic": "Paweł",
        "birth_date": "1991-11-18",
        "gender_i_c": "male",
        "phone_no_i_c": "+393451214623",
        "email": "email333@mail.com",
    }


@pytest.fixture
def record_files() -> dict:
    return {
        "individuals": [
            {
                "disability_id_photo_i_c": "/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAP///////////////////////////////////"
                "///////////////////////////////////////////////////wgALCAABAAEBAREA/8Q"
                "AFBABAAAAAAAAAAAAAAAAAAAAAP/aAAgBAQABPxA=",
            }
        ],
    }


@pytest.mark.parametrize(
    ("admin1_h_c", "admin2_h_c", "admin3_h_c", "admin4_h_c"),
    [
        ("UA07", "UA0702", "UA0114007", "UA0114007"),
        (None, None, None, "UA0114007"),
        (None, None, "UA0114007", None),
        (None, "UA0702", None, None),
    ],
)
def test_import_data_to_datahub(
    admin1_h_c: str | None,
    admin2_h_c: str | None,
    admin3_h_c: str | None,
    admin4_h_c: str | None,
    ukraine_admin_areas: dict,
    document_types: dict,
    registration: object,
    user: object,
    record_defaults: dict,
    base_household: list[dict],
    individual_with_bank_account_and_tax_and_disability: dict,
    individual_with_bank_account_and_tax: dict,
    individual_with_no_tax: dict,
    individual_without_bank_account: dict,
    individual_with_tax_id_which_is_too_long: dict,
    record_files: dict,
) -> None:
    assert ukraine_admin_areas
    assert document_types
    household = copy.deepcopy(base_household)
    household[0]["admin1_h_c"] = admin1_h_c
    household[0]["admin2_h_c"] = admin2_h_c
    household[0]["admin3_h_c"] = admin3_h_c
    household[0]["admin4_h_c"] = admin4_h_c

    records = [
        RecordFactory(
            **record_defaults,
            source_id=1,
            fields={"household": household, "individuals": [individual_with_bank_account_and_tax_and_disability]},
            files=json.dumps(record_files).encode(),
        ),
        RecordFactory(
            **record_defaults,
            source_id=2,
            fields={"household": household, "individuals": [individual_with_bank_account_and_tax]},
            files=json.dumps({}).encode(),
        ),
        RecordFactory(
            **record_defaults,
            source_id=3,
            fields={"household": household, "individuals": [individual_with_no_tax]},
            files=json.dumps(record_files).encode(),
        ),
        RecordFactory(
            **record_defaults,
            source_id=4,
            fields={"household": household, "individuals": [individual_without_bank_account]},
            files=json.dumps(record_files).encode(),
        ),
    ]
    RecordFactory(
        **record_defaults,
        source_id=5,
        fields={"household": household, "individuals": [individual_with_tax_id_which_is_too_long]},
        files=json.dumps(record_files).encode(),
    )

    service = GenericRegistrationService(registration)
    rdi = service.create_rdi(user, f"generic rdi {datetime.datetime.now()}")
    records_ids = [record.id for record in records]
    service.process_records(rdi.id, records_ids)

    assert Record.objects.filter(id__in=records_ids, ignored=False).count() == 4
    assert PendingHousehold.objects.count() == 4
    assert PendingHousehold.objects.filter(program=rdi.program).count() == 4
    assert (
        PendingDocument.objects.filter(
            document_number="TESTID",
            type__key=IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_TAX_ID],
        ).count()
        == 1
    )
    assert (
        PendingDocument.objects.filter(
            document_number="TESTID",
            type__key=IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_TAX_ID],
            program=rdi.program,
        ).count()
        == 1
    )

    pending_household = PendingHousehold.objects.first()
    assert pending_household
    registration_data_import = pending_household.registration_data_import
    assert "ff" in pending_household.flex_fields
    assert registration_data_import.program == rdi.program

    assert PendingIndividualRoleInHousehold.objects.filter(role=ROLE_PRIMARY).count() == 1
    assert PendingIndividualRoleInHousehold.objects.filter(role=ROLE_ALTERNATE).count() == 1


def test_import_data_to_datahub_household_individual(
    ukraine_admin_areas: dict,
    document_types: dict,
    registration: object,
    user: object,
    record_defaults: dict,
    base_household: list[dict],
    individual_with_bank_account_and_tax_and_disability: dict,
    record_files: dict,
) -> None:
    assert ukraine_admin_areas
    assert document_types
    records = [
        RecordFactory(
            **record_defaults,
            source_id=1,
            fields={
                "household": base_household,
                "individuals": [individual_with_bank_account_and_tax_and_disability],
                "enumerators": "ABC",
                "marketing": {"can_unicef_contact_you": "YES"},
            },
            files=json.dumps(record_files).encode(),
        ),
    ]
    service = GenericRegistrationService(registration)
    rdi = service.create_rdi(user, f"generic rdi {datetime.datetime.now()}")
    records_ids = [record.id for record in records]
    service.process_records(rdi.id, records_ids)

    assert Record.objects.filter(id__in=records_ids, ignored=False).count() == 1
    assert PendingHousehold.objects.count() == 1

    household = PendingHousehold.objects.first()
    assert household
    assert household.zip_code == "00126"
    assert household.flex_fields["ff"] == "random"
    assert household.flex_fields["enumerators"] == "ABC"
    assert household.flex_fields["marketing_can_unicef_contact_you"] == "YES"

    assert PendingDocument.objects.get(document_number="123123123", type__key="tax_id")
    assert PendingDocument.objects.get(document_number="xyz", type__key="disability_certificate")
    assert PendingIndividual.objects.get(
        given_name="Jan",
        middle_name="Roman",
        family_name="Romaniak",
        relationship="HEAD",
        sex="MALE",
        email="email123@mail.com",
        phone_no="+393892781511",
        pregnant=True,
    )
    assert PendingIndividualRoleInHousehold.objects.filter(role=ROLE_PRIMARY).count() == 1
