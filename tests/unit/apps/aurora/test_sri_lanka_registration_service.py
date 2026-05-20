import datetime
import json
from typing import Any

from django.utils import timezone
from freezegun import freeze_time
import pytest

from extras.test_utils.factories.account import UserFactory
from extras.test_utils.factories.aurora import OrganizationFactory, ProjectFactory, RecordFactory, RegistrationFactory
from extras.test_utils.factories.core import BusinessAreaFactory, DataCollectingTypeFactory
from extras.test_utils.factories.geo import AreaFactory, AreaTypeFactory, CountryFactory
from extras.test_utils.factories.household import DocumentTypeFactory
from extras.test_utils.factories.program import ProgramFactory
from hope.apps.core.utils import IDENTIFICATION_TYPE_TO_KEY_MAPPING
from hope.apps.household.const import IDENTIFICATION_TYPE_NATIONAL_ID
from hope.contrib.aurora.models import Record
from hope.contrib.aurora.services.sri_lanka_flex_registration_service import SriLankaRegistrationService
from hope.models import (
    Area,
    DataCollectingType,
    PendingDocument,
    PendingHousehold,
    PendingIndividual,
    PendingIndividualRoleInHousehold,
    Program,
)

pytestmark = [pytest.mark.django_db, pytest.mark.usefixtures("mock_elasticsearch")]


@pytest.fixture
def business_area() -> Any:
    return BusinessAreaFactory(slug="sri-lanka2")


@pytest.fixture
def data_collecting_type(business_area: Any) -> DataCollectingType:
    data_collecting_type = DataCollectingTypeFactory(label="SizeOnlyXYZ", code="size_onlyXYZ")
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
def sri_lanka_country() -> Any:
    return CountryFactory(name="Sri Lanka", short_name="Sri Lanka", iso_code2="LK", iso_code3="LKA", iso_num="0144")


@pytest.fixture
def sri_lanka_admin_areas(sri_lanka_country: Any) -> dict[str, Any]:
    area_type1 = AreaTypeFactory(country=sri_lanka_country, name="admin1", area_level=1)
    area_type2 = AreaTypeFactory(country=sri_lanka_country, name="admin2", area_level=2)
    area_type3 = AreaTypeFactory(country=sri_lanka_country, name="admin3", area_level=3)
    area_type4 = AreaTypeFactory(country=sri_lanka_country, name="admin4", area_level=4)

    admin1 = AreaFactory(name="SriLanka admin1", p_code="LK1", area_type=area_type1)
    admin2 = AreaFactory(name="SriLanka admin2", p_code="LK11", area_type=area_type2, parent=admin1)
    admin3 = AreaFactory(name="SriLanka admin3", p_code="LK1163", area_type=area_type3, parent=admin2)
    admin4 = AreaFactory(name="SriLanka admin4", p_code="LK1163020", area_type=area_type4, parent=admin3)
    Area.objects.rebuild()
    return {"admin1": admin1, "admin2": admin2, "admin3": admin3, "admin4": admin4}


@pytest.fixture
def national_id_document_type() -> Any:
    return DocumentTypeFactory(
        key=IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_NATIONAL_ID],
        label=IDENTIFICATION_TYPE_NATIONAL_ID,
    )


@pytest.fixture
def sri_lanka_records(registration: Any, sri_lanka_admin_areas: dict[str, Any]) -> list[Record]:
    children_info = [
        {
            "gender_i_c": "male",
            "full_name_i_c": "Alexis",
            "birth_date_i_c": "2022-01-04",
            "relationship_i_c": "son_daughter",
        }
    ]

    caretaker_info = [
        {
            "gender_i_c": "   female",
            "full_name_i_c": "Alexis",
            "birth_date_i_c": "1989-01-04",
            "has_nic_number_i_c": "n",
            "who_answers_phone_i_c": "mother/caretaker",
        }
    ]

    collector_info = [
        {
            "gender_i_c": " male",
            "phone_no_i_c": "+94788908046",
            "email": "email999@mail.com",
            "full_name_i_c": "Dome",
            "birth_date_i_c": "1980-01-04",
            "relationship_i_c": "brother_sister",
            "confirm_nic_number": "123456789V",
            "national_id_no_i_c": "123456789V",
            "branch_or_branch_code": "7472_002",
            "account_holder_name_i_c": "Test Holder Name 123",
            "who_answers_this_phone": "alternate collector",
            "confirm_alternate_collector_phone_number": "+94788908046",
            "does_the_mothercaretaker_have_her_own_active_bank_account_not_samurdhi": "n",
        }
    ]

    localization_info = [
        {
            "admin2_h_c": sri_lanka_admin_areas["admin2"].p_code,
            "admin3_h_c": sri_lanka_admin_areas["admin3"].p_code,
            "admin4_h_c": sri_lanka_admin_areas["admin4"].p_code,
            "address_h_c": "Alexis",
            "moh_center_of_reference": "MOH279",
        }
    ]

    timestamp = timezone.make_aware(datetime.datetime(2022, 4, 1))
    empty_files = json.dumps({}).encode()
    record1 = RecordFactory(
        registration=registration.source_id,
        timestamp=timestamp,
        source_id=1,
        fields={
            "children-info": children_info,
            "id_enumerator": "1992",
            "caretaker-info": caretaker_info,
            "collector-info": collector_info,
            "localization-info": localization_info,
            "prefered_language_of_contact": "ta",
        },
        files=empty_files,
    )
    record2 = RecordFactory(
        registration=registration.source_id,
        timestamp=timestamp,
        source_id=2,
        fields={},
        status=Record.STATUS_IMPORTED,
        files=empty_files,
    )
    return [record1, record2]


@freeze_time("2023-12-12")
def test_import_data_to_datahub(
    registration: Any,
    user: Any,
    program: Program,
    sri_lanka_country: Any,
    national_id_document_type: Any,
    sri_lanka_records: list[Record],
) -> None:
    service = SriLankaRegistrationService(registration)
    rdi = service.create_rdi(user, f"sri_lanka rdi {datetime.datetime.now()}")
    records_ids = [record.id for record in sri_lanka_records]
    service.process_records(rdi.id, records_ids)

    sri_lanka_records[0].refresh_from_db()
    assert Record.objects.filter(id__in=records_ids, ignored=False, status=Record.STATUS_IMPORTED).count() == 2

    assert PendingHousehold.objects.count() == 1
    assert PendingHousehold.objects.filter(program=rdi.program).count() == 1
    assert PendingIndividualRoleInHousehold.objects.count() == 1
    assert PendingDocument.objects.count() == 1
    assert PendingDocument.objects.filter(program=rdi.program).count() == 1

    household = PendingHousehold.objects.first()
    assert household.admin1.p_code == "LK1"
    assert household.admin2.p_code == "LK11"
    assert household.admin3.p_code == "LK1163"
    assert household.admin4.p_code == "LK1163020"
    assert household.admin_area.p_code == "LK1163020"

    registration_data_import = household.registration_data_import
    assert registration_data_import.program == program

    assert PendingIndividual.objects.filter(relationship="HEAD").first().flex_fields == {"has_nic_number_i_c": "n"}

    assert PendingIndividual.objects.filter(full_name="Dome").first().flex_fields == {
        "confirm_nic_number": "123456789V",
        "branch_or_branch_code": "7472_002",
        "who_answers_this_phone": "alternate collector",
        "confirm_alternate_collector_phone_number": "+94788908046",
        "does_the_mothercaretaker_have_her_own_active_bank_account_not_samurdhi": "n",
    }
    assert PendingIndividual.objects.filter(full_name="Dome").first().email == "email999@mail.com"
    assert PendingIndividual.objects.filter(full_name="Dome").first().age_at_registration == 43
    assert PendingIndividual.objects.filter(full_name="Dome", program=rdi.program).first().age_at_registration == 43


def test_import_record_twice(
    registration: Any,
    user: Any,
    sri_lanka_country: Any,
    national_id_document_type: Any,
    sri_lanka_records: list[Record],
) -> None:
    service = SriLankaRegistrationService(registration)
    rdi = service.create_rdi(user, f"sri_lanka rdi {datetime.datetime.now()}")

    service.process_records(rdi.id, [sri_lanka_records[0].id])
    sri_lanka_records[0].refresh_from_db()

    assert Record.objects.first().status == Record.STATUS_IMPORTED
    assert PendingHousehold.objects.count() == 1

    service.process_records(rdi.id, [sri_lanka_records[0].id])
    sri_lanka_records[0].refresh_from_db()
    assert PendingHousehold.objects.count() == 1
