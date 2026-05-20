import datetime
import json
from typing import Any

from django.utils import timezone
import pytest

from extras.test_utils.factories.account import UserFactory
from extras.test_utils.factories.aurora import OrganizationFactory, ProjectFactory, RecordFactory, RegistrationFactory
from extras.test_utils.factories.core import BusinessAreaFactory, DataCollectingTypeFactory
from extras.test_utils.factories.geo import AreaFactory, AreaTypeFactory, CountryFactory
from extras.test_utils.factories.household import DocumentTypeFactory
from extras.test_utils.factories.program import ProgramFactory
from hope.apps.core.utils import IDENTIFICATION_TYPE_TO_KEY_MAPPING
from hope.apps.household.const import IDENTIFICATION_TYPE_TAX_ID
from hope.contrib.aurora.models import Record
from hope.contrib.aurora.services.ukraine_flex_registration_service import (
    Registration2024,
    UkraineBaseRegistrationService,
)
from hope.models import Area, DataCollectingType, PendingDocument, PendingHousehold, PendingIndividual, Program

pytestmark = [pytest.mark.django_db, pytest.mark.usefixtures("mock_elasticsearch")]


@pytest.fixture
def business_area() -> Any:
    return BusinessAreaFactory(slug="some-ukraine-slug")


@pytest.fixture
def data_collecting_type(business_area: Any) -> DataCollectingType:
    data_collecting_type = DataCollectingTypeFactory(label="SomeFull", code="some_full")
    data_collecting_type.limit_to.add(business_area)
    return data_collecting_type


@pytest.fixture
def program(business_area: Any, data_collecting_type: DataCollectingType) -> Program:
    return ProgramFactory(
        status=Program.ACTIVE,
        business_area=business_area,
        data_collecting_type=data_collecting_type,
    )


@pytest.fixture
def organization(business_area: Any) -> Any:
    return OrganizationFactory(business_area=business_area, slug=business_area.slug)


@pytest.fixture
def project(organization: Any, program: Program) -> Any:
    return ProjectFactory(name="fake_project", organization=organization, programme=program)


@pytest.fixture
def registration(project: Any) -> Any:
    return RegistrationFactory(name="fake_registration", project=project)


@pytest.fixture
def user() -> Any:
    return UserFactory()


@pytest.fixture
def ukraine_country() -> Any:
    return CountryFactory(name="Ukraine", short_name="Ukraine", iso_code2="UA", iso_code3="UKR", iso_num="0804")


@pytest.fixture
def ukraine_admin_areas(ukraine_country: Any) -> dict[str, Any]:
    area_type1 = AreaTypeFactory(country=ukraine_country, name="admin1", area_level=1)
    area_type2 = AreaTypeFactory(country=ukraine_country, name="admin2", area_level=2)
    area_type3 = AreaTypeFactory(country=ukraine_country, name="admin3", area_level=3)
    admin1 = AreaFactory(p_code="UA07", name="Name1", area_type=area_type1)
    admin2 = AreaFactory(p_code="UA0702", name="Name2", parent=admin1, area_type=area_type2)
    admin3 = AreaFactory(p_code="UA0702001", name="Name3", parent=admin2, area_type=area_type3)
    Area.objects.rebuild()
    return {"admin1": admin1, "admin2": admin2, "admin3": admin3}


@pytest.fixture
def tax_id_document_type() -> Any:
    return DocumentTypeFactory(
        key=IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_TAX_ID],
        label=IDENTIFICATION_TYPE_TAX_ID,
    )


@pytest.fixture
def ukraine_household() -> list[dict[str, Any]]:
    return [
        {
            "residence_status_h_c": "non_host",
            "where_are_you_now": "",
            "admin1_h_c": "UA07",
            "admin2_h_c": "UA0702",
            "admin3_h_c": "UA0702001",
            "size_h_c": 5,
        }
    ]


@pytest.fixture
def ukraine_individual_payloads() -> dict[str, dict[str, Any]]:
    return {
        "with_tax_and_disability": {
            "tax_id_no_i_c": "123123123",
            "relationship_i_c": "head",
            "given_name_i_c": "Jan",
            "family_name_i_c": "Romaniak",
            "patronymic": "Roman",
            "birth_date": "1991-11-18",
            "gender_i_c": "male",
            "phone_no_i_c": "0501706662",
            "email": "email123@mail.com",
        },
        "with_tax": {
            "tax_id_no_i_c": "123123123",
            "relationship_i_c": "head",
            "given_name_i_c": "Wiktor",
            "family_name_i_c": "Lamiący",
            "patronymic": "Stefan",
            "birth_date": "1991-11-18",
            "gender_i_c": "male",
            "phone_no_i_c": "0501706662",
            "email": "email321@mail.com",
        },
        "no_tax": {
            "tax_id_no_i_c": "",
            "relationship_i_c": "head",
            "given_name_i_c": "Michał",
            "family_name_i_c": "Brzęczący",
            "patronymic": "Janusz",
            "birth_date": "1991-11-18",
            "gender_i_c": "male",
            "phone_no_i_c": "0501706662",
            "email": "email111@mail.com",
        },
        "without_bank_account": {
            "tax_id_no_i_c": "TESTID",
            "relationship_i_c": "head",
            "given_name_i_c": "Aleksiej",
            "family_name_i_c": "Prysznicow",
            "patronymic": "Paweł",
            "birth_date": "1991-11-18",
            "gender_i_c": "male",
            "phone_no_i_c": "0501706662",
            "email": "email222@mail.com",
        },
        "tax_too_long": {
            "tax_id_no_i_c": "x" * 300,
            "relationship_i_c": "head",
            "given_name_i_c": "Aleksiej",
            "family_name_i_c": "Prysznicow",
            "patronymic": "Paweł",
            "birth_date": "1991-11-18",
            "gender_i_c": "male",
            "phone_no_i_c": "0501706662",
            "email": "email333@mail.com",
        },
    }


@pytest.fixture
def ukraine_files() -> dict[str, Any]:
    return {
        "individuals": [
            {
                "disability_certificate_picture": "/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAP//////////////////////////////////////////////////////////////////////////////////////wgALCAABAAEBAREA/8QAFBABAAAAAAAAAAAAAAAAAAAAAP/aAAgBAQABPxA=",  # noqa
            }
        ]
    }


@pytest.fixture
def ukraine_records(
    registration: Any,
    ukraine_household: list[dict[str, Any]],
    ukraine_individual_payloads: dict[str, dict[str, Any]],
    ukraine_files: dict[str, Any],
) -> dict[str, list[Record]]:
    timestamp = timezone.make_aware(datetime.datetime(2022, 4, 1))
    files_blob = json.dumps(ukraine_files).encode()

    records = [
        RecordFactory(
            registration=registration.source_id,
            timestamp=timestamp,
            source_id=1,
            fields={
                "household": ukraine_household,
                "individuals": [ukraine_individual_payloads["with_tax_and_disability"]],
            },
            files=files_blob,
        ),
        RecordFactory(
            registration=registration.source_id,
            timestamp=timestamp,
            source_id=2,
            fields={
                "household": ukraine_household,
                "individuals": [ukraine_individual_payloads["with_tax"]],
            },
            files=json.dumps({}).encode(),
        ),
        RecordFactory(
            registration=registration.source_id,
            timestamp=timestamp,
            source_id=3,
            fields={
                "household": ukraine_household,
                "individuals": [ukraine_individual_payloads["no_tax"]],
            },
            files=files_blob,
        ),
        RecordFactory(
            registration=registration.source_id,
            timestamp=timestamp,
            source_id=4,
            fields={
                "household": ukraine_household,
                "individuals": [ukraine_individual_payloads["without_bank_account"]],
            },
            files=files_blob,
        ),
    ]
    bad_records = [
        RecordFactory(
            registration=registration.source_id,
            timestamp=timestamp,
            source_id=5,
            fields={
                "household": ukraine_household,
                "individuals": [ukraine_individual_payloads["tax_too_long"]],
            },
            files=files_blob,
        )
    ]
    return {"records": records, "bad_records": bad_records}


@pytest.fixture
def registration_2024_record(
    registration: Any,
    ukraine_household: list[dict[str, Any]],
    ukraine_individual_payloads: dict[str, dict[str, Any]],
) -> Record:
    timestamp = timezone.make_aware(datetime.datetime(2024, 2, 4))
    individual = {
        **ukraine_individual_payloads["with_tax_and_disability"],
        "low_income_hh_h_f": True,
        "single_headed_hh_h_f": False,
    }
    return RecordFactory(
        registration=registration.source_id,
        timestamp=timestamp,
        source_id=6,
        fields={
            "household": ukraine_household,
            "individuals": [individual],
        },
        files=json.dumps({}).encode(),
    )


def test_import_data_to_datahub(
    registration: Any,
    user: Any,
    program: Program,
    ukraine_country: Any,
    ukraine_admin_areas: dict[str, Any],
    tax_id_document_type: Any,
    ukraine_records: dict[str, list[Record]],
) -> None:
    service = UkraineBaseRegistrationService(registration)
    rdi = service.create_rdi(user, f"ukraine rdi {datetime.datetime.now()}")
    records_ids = [record.id for record in ukraine_records["records"]]
    service.process_records(rdi.id, records_ids)

    ukraine_records["records"][2].refresh_from_db()
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

    registration_data_import = PendingHousehold.objects.all()[0].registration_data_import
    assert registration_data_import.program == program


def test_import_data_to_datahub_retry(
    registration: Any,
    user: Any,
    ukraine_country: Any,
    ukraine_admin_areas: dict[str, Any],
    tax_id_document_type: Any,
    ukraine_records: dict[str, list[Record]],
) -> None:
    service = UkraineBaseRegistrationService(registration)
    rdi = service.create_rdi(user, f"ukraine rdi {datetime.datetime.now()}")
    records_ids_all = [record.id for record in ukraine_records["records"]]
    service.process_records(rdi.id, records_ids_all)
    ukraine_records["records"][2].refresh_from_db()
    assert Record.objects.filter(id__in=records_ids_all, ignored=False).count() == 4
    assert PendingHousehold.objects.count() == 4

    service = UkraineBaseRegistrationService(registration)
    rdi = service.create_rdi(user, f"ukraine rdi {datetime.datetime.now()}")
    records_ids = [record.id for record in ukraine_records["records"][:2]]
    service.process_records(rdi.id, records_ids)
    assert Record.objects.filter(id__in=records_ids_all, ignored=False).count() == 4
    assert PendingHousehold.objects.count() == 4


def test_import_document_validation(
    registration: Any,
    user: Any,
    ukraine_country: Any,
    ukraine_admin_areas: dict[str, Any],
    tax_id_document_type: Any,
    ukraine_records: dict[str, list[Record]],
) -> None:
    service = UkraineBaseRegistrationService(registration)
    rdi = service.create_rdi(user, f"ukraine rdi {datetime.datetime.now()}")

    service.process_records(rdi.id, [record.id for record in ukraine_records["bad_records"]])
    ukraine_records["bad_records"][0].refresh_from_db()
    assert ukraine_records["bad_records"][0].status == Record.STATUS_ERROR
    assert PendingHousehold.objects.count() == 0


def test_registration_2024_import_data_to_datahub(
    registration: Any,
    user: Any,
    ukraine_country: Any,
    ukraine_admin_areas: dict[str, Any],
    tax_id_document_type: Any,
    registration_2024_record: Record,
) -> None:
    service = Registration2024(registration)
    rdi = service.create_rdi(user, f"ukraine rdi {datetime.datetime.now()}")
    service.process_records(rdi.id, [registration_2024_record.id])

    assert Record.objects.filter(id__in=[registration_2024_record.id], ignored=False).count() == 1
    assert PendingHousehold.objects.count() == 1
    assert PendingIndividual.objects.count() == 1
    assert PendingIndividual.objects.filter(program=rdi.program).count() == 1
    assert PendingIndividual.objects.get(family_name="Romaniak").flex_fields == {
        "low_income_hh_h_f": True,
        "single_headed_hh_h_f": False,
    }
