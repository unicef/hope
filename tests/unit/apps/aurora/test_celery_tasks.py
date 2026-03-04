import base64
from contextlib import contextmanager
import datetime
import json
from typing import Any, Callable, Optional
from unittest.mock import patch
import uuid

from django.utils import timezone
import pytest

from extras.test_utils.factories import (
    AreaFactory,
    AreaTypeFactory,
    BusinessAreaFactory,
    CountryFactory,
    DocumentTypeFactory,
    OrganizationFactory,
    ProgramFactory,
    ProjectFactory,
    RegistrationFactory,
)
from hope.apps.core.utils import IDENTIFICATION_TYPE_TO_KEY_MAPPING
from hope.apps.household.const import (
    DISABLED,
    FEMALE,
    HEAD,
    IDENTIFICATION_TYPE_BANK_STATEMENT,
    IDENTIFICATION_TYPE_BIRTH_CERTIFICATE,
    IDENTIFICATION_TYPE_NATIONAL_ID,
    IDENTIFICATION_TYPE_TAX_ID,
    MALE,
    NOT_DISABLED,
    SON_DAUGHTER,
)
from hope.contrib.aurora.celery_tasks import automate_rdi_creation_task, process_flex_records_task
from hope.contrib.aurora.models import Record
from hope.contrib.aurora.services.flex_registration_service import create_task_for_processing_records
from hope.contrib.aurora.services.sri_lanka_flex_registration_service import SriLankaRegistrationService
from hope.contrib.aurora.services.ukraine_flex_registration_service import (
    UkraineBaseRegistrationService,
    UkraineRegistrationService,
)
from hope.models import PendingDocument, PendingHousehold, PendingIndividual, Program, RegistrationDataImport

pytestmark = pytest.mark.django_db

SRI_LANKA_FIELDS: dict = {
    "caretaker-info": [
        {
            "birth_date_i_c": "1992-07-27",
            "confirm_phone_number": "+94715880855",
            "full_name_i_c": "M.T.M.Banu",
            "gender_i_c": "female",
            "has_nic_number_i_c": "y",
            "national_id_no_i_c": "927091615V",
            "phone_no_i_c": "+94715880855",
            "please_confirm_nic_number": "927091615V",
            "who_answers_phone_i_c": "mother/caretaker",
            "email": "collector-email@mail.com",
        }
    ],
    "children-info": [
        {
            "birth_date_i_c": "2022-04-22",
            "chidlren_birth_certificate": "6331-Nawanagaraya",
            "full_name_i_c": "M.S.Rayaan",
            "gender_i_c": "male",
            "relationship_i_c": "son_daughter",
        }
    ],
    "collector-info": [
        {
            "does_the_mothercaretaker_have_her_own_active_bank_account_not_samurdhi": "y",
        }
    ],
    "id_enumerator": "2085",
    "localization-info": [
        {
            "address_h_c": "Alahaperumagama,Vijithapura",
            "admin2_h_c": "LK11",
            "admin3_h_c": "LK1163",
            "admin4_h_c": "LK1163020",
            "moh_center_of_reference": "MOH279",
        }
    ],
    "prefered_language_of_contact": "si",
}

UKRAINE_FIELDS: dict = {
    "household": [
        {
            "residence_status_h_c": "non_host",
            "where_are_you_now": "",
            "admin1_h_c": "UA07",
            "admin2_h_c": "UA0702",
            "admin3_h_c": "UA0702001",
            "size_h_c": 5,
        }
    ],
    "individuals": [
        {
            "given_name_i_c": "Natalia",
            "family_name_i_c": "Sapiga",
            "patronymic": "Adamivna",
            "birth_date": "1983-09-24",
            "gender_i_c": "female",
            "relationship_i_c": "head",
            "disability_i_c": "y",
            "disabiliyt_recognize_i_c": "y",
            "phone_no_i_c": "0636060474",
            "email": "fake-email-123@mail.com",
            "q1": "",
            "tax_id_no_i_c": "123123123",
            "national_id_no_i_c_1": "",
            "international_passport_i_c": "",
            "drivers_license_no_i_c": "",
            "birth_certificate_no_i_c": "",
            "residence_permit_no_i_c": "",
            "role_i_c": "y",
        }
    ],
}

UKRAINE_NEW_FORM_FIELDS: dict = {
    "ip": "176.113.164.17",
    "counters": {
        "start": "Thu Mar 23 2023 14:26:07 GMT+0200 (Eastern European Standard Time)",
        "total": "71464926",
        "rounds": "1",
        "elapsed": "71464926",
    },
    "enumerator": "655384",
    "household": [{"admin1_h_c": "UA14", "admin2_h_c": "UA1408", "admin3_h_c": "UA1408005"}],
    "marketing": [{"can_unicef_contact_you": [{}]}],
    "individuals": [
        {
            "id_type": "tax_id",
            "role_i_c": "y",
            "birth_date": "1990-11-11",
            "gender_i_c": "male",
            "patronymic": "Viktorovich",
            "phone_no_i_c": "+380952025248",
            "tax_id_no_i_c": "123465432321321",
            "disability_i_c": "n",
            "given_name_i_c": "Pavlo",
            "family_name_i_c": "Mok",
            "relationship_i_c": "head",
        },
        {
            "birth_date": "2023-03-06",
            "gender_i_c": "female",
            "patronymic": "Petrovich",
            "disability_i_c": "y",
            "given_name_i_c": "Stefania",
            "family_name_i_c": "Bandera",
            "relationship_i_c": "son_daughter",
            "verified_disability": "1",
            "birth_certificate_no_i_c": "I-ASD-454511",
        },
    ],
    "validator_uk": [{"validation": "y"}],
}

UKRAINE_NEW_FORM_FILES: dict = {
    "individuals": [
        {},  # no files for first Individual
        {
            "disability_certificate_picture": str(base64.b64encode(b"h\x65llo"), "utf-8"),
            "birth_certificate_picture": str(base64.b64encode(b"h\x65llo"), "utf-8"),
        },
    ],
}


class ServiceWithoutCeleryTask:
    process_flex_records_task = None


@pytest.fixture
def record_factory() -> Callable[..., Record]:
    def _create_record(
        *,
        fields: dict,
        registration: int,
        status: str,
        files: Optional[dict] = None,
        source_id: int = 1,
    ) -> Record:
        files_payload = json.dumps(files).encode() if files is not None else None
        return Record.objects.create(
            registration=registration,
            status=status,
            timestamp=timezone.now(),
            data=None,
            source_id=source_id,
            fields=fields,
            files=files_payload,
        )

    return _create_record


@pytest.fixture
def ukraine_context() -> dict[str, object]:
    business_area = BusinessAreaFactory(
        name="Ukraine",
        long_name="the long name of ukraine",
        region_code="3245",
        region_name="UA",
        has_data_sharing_agreement=True,
        active=True,
    )
    country = CountryFactory(name="Ukraine", short_name="Ukraine", iso_code2="UA", iso_code3="UKR", iso_num="0804")
    for document_key in UkraineBaseRegistrationService.DOCUMENT_MAPPING_KEY_DICT:
        DocumentTypeFactory(key=document_key, label=document_key)
    admin1_type = AreaTypeFactory(area_level=1, country=country)
    admin2_type = AreaTypeFactory(area_level=2, country=country)
    admin3_type = AreaTypeFactory(area_level=3, country=country)
    admin1 = AreaFactory(p_code="UA07", name="Name1", area_type=admin1_type)
    admin2 = AreaFactory(p_code="UA0702", name="Name2", parent=admin1, area_type=admin2_type)
    AreaFactory(p_code="UA0702001", name="Name3", parent=admin2, area_type=admin3_type)
    admin1_new = AreaFactory(p_code="UA14", name="Name4", area_type=admin1_type)
    admin2_new = AreaFactory(p_code="UA1408", name="Name5", parent=admin1_new, area_type=admin2_type)
    AreaFactory(p_code="UA1408005", name="Name6", parent=admin2_new, area_type=admin3_type)

    program = ProgramFactory(status=Program.ACTIVE, business_area=business_area)
    organization = OrganizationFactory(name=business_area.slug, slug=business_area.slug, business_area=business_area)
    project = ProjectFactory(organization=organization, programme=program)
    registration = RegistrationFactory(project=project, rdi_parser=UkraineBaseRegistrationService)

    return {
        "business_area": business_area,
        "program": program,
        "organization": organization,
        "project": project,
        "registration": registration,
    }


@pytest.fixture
def run_automate_rdi_creation_task() -> Callable[..., list]:
    @contextmanager
    def unlocked_cache(*_args: Any, **_kwargs: Any) -> Any:
        yield True

    def _run(*args: Any, **kwargs: Any) -> list:
        with patch(
            "hope.contrib.aurora.celery_tasks.locked_cache",
            unlocked_cache,
        ):
            return automate_rdi_creation_task(*args, **kwargs)

    return _run


def test_successful_run_without_records_to_import(
    ukraine_context: dict[str, object], run_automate_rdi_creation_task: Callable[..., list]
) -> None:
    registration = ukraine_context["registration"]

    result = run_automate_rdi_creation_task(registration_id=registration.source_id, page_size=1)

    assert result[0] == "No Records found"


def test_not_running_with_record_status_not_to_import(
    ukraine_context: dict[str, object],
    record_factory: Callable[..., Record],
    run_automate_rdi_creation_task: Callable[..., list],
) -> None:
    registration = ukraine_context["registration"]
    record_factory(
        fields=UKRAINE_FIELDS,
        registration=registration.source_id,
        status=Record.STATUS_ERROR,
    )

    assert RegistrationDataImport.objects.count() == 0
    assert PendingIndividual.objects.count() == 0

    result = run_automate_rdi_creation_task(registration_id=registration.source_id, page_size=1)

    assert RegistrationDataImport.objects.count() == 0
    assert PendingIndividual.objects.count() == 0
    assert result[0] == "No Records found"


def test_successful_run_with_records_to_import(
    ukraine_context: dict[str, object],
    record_factory: Callable[..., Record],
    run_automate_rdi_creation_task: Callable[..., list],
) -> None:
    registration = ukraine_context["registration"]
    amount_of_records = 10
    page_size = 3

    for _ in range(amount_of_records):
        record_factory(
            fields=UKRAINE_FIELDS,
            registration=registration.source_id,
            status=Record.STATUS_TO_IMPORT,
        )

    assert Record.objects.count() == amount_of_records
    assert RegistrationDataImport.objects.count() == 0
    assert PendingIndividual.objects.count() == 0

    result = run_automate_rdi_creation_task(
        registration_id=registration.source_id,
        page_size=page_size,
        template="some template {date} {records}",
    )

    assert RegistrationDataImport.objects.count() == 4
    assert PendingIndividual.objects.count() == amount_of_records
    assert result[0][0].startswith("some template")
    assert result[0][1] == page_size
    assert result[1][1] == page_size
    assert result[2][1] == page_size
    assert result[3][1] == amount_of_records - 3 * page_size


def test_successful_run_and_automatic_merge(
    ukraine_context: dict[str, object],
    record_factory: Callable[..., Record],
    run_automate_rdi_creation_task: Callable[..., list],
) -> None:
    registration = ukraine_context["registration"]
    amount_of_records = 10
    page_size = 3

    for _ in range(amount_of_records):
        record_factory(
            fields=UKRAINE_FIELDS,
            registration=registration.source_id,
            status=Record.STATUS_TO_IMPORT,
        )

    assert Record.objects.count() == amount_of_records
    assert RegistrationDataImport.objects.count() == 0
    assert PendingIndividual.objects.count() == 0

    with patch("hope.contrib.aurora.celery_tasks.merge_registration_data_import_task.delay") as merge_task_mock:
        result = run_automate_rdi_creation_task(
            registration_id=registration.source_id,
            page_size=page_size,
            template="some template {date} {records}",
            auto_merge=True,
        )

    assert len(result) == 4
    assert merge_task_mock.called


def test_successful_run_and_fix_task_id(
    ukraine_context: dict[str, object],
    record_factory: Callable[..., Record],
    run_automate_rdi_creation_task: Callable[..., list],
) -> None:
    registration = ukraine_context["registration"]
    amount_of_records = 10
    page_size = 3

    for _ in range(amount_of_records):
        record_factory(
            fields=UKRAINE_FIELDS,
            registration=registration.source_id,
            status=Record.STATUS_TO_IMPORT,
        )

    assert Record.objects.count() == amount_of_records
    assert RegistrationDataImport.objects.count() == 0
    assert PendingIndividual.objects.count() == 0

    with patch("hope.contrib.aurora.celery_tasks.merge_registration_data_import_task.delay") as merge_task_mock:
        result = run_automate_rdi_creation_task(
            registration_id=registration.source_id,
            page_size=page_size,
            template="some template {date} {records}",
            fix_tax_id=True,
        )

    assert len(result) == 4
    assert not merge_task_mock.called
    assert set(Record.objects.values_list("unique_field", flat=True)) == {"123123123"}


@pytest.mark.parametrize(
    ("registration_id", "fields", "files", "expected_individuals_per_record"),
    [
        (2, UKRAINE_FIELDS, None, 1),
        (3, UKRAINE_FIELDS, None, 1),
        (21, UKRAINE_NEW_FORM_FIELDS, UKRAINE_NEW_FORM_FILES, 2),
        (26, UKRAINE_NEW_FORM_FIELDS, UKRAINE_NEW_FORM_FILES, 2),
        (27, UKRAINE_NEW_FORM_FIELDS, UKRAINE_NEW_FORM_FILES, 2),
        (28, UKRAINE_NEW_FORM_FIELDS, UKRAINE_NEW_FORM_FILES, 2),
        (29, UKRAINE_NEW_FORM_FIELDS, UKRAINE_NEW_FORM_FILES, 2),
    ],
)
def test_with_different_registration_ids_ukraine(
    registration_id: int,
    fields: dict,
    files: Optional[dict],
    expected_individuals_per_record: int,
    record_factory: Callable[..., Record],
    run_automate_rdi_creation_task: Callable[..., list],
    ukraine_context: dict[str, object],
) -> None:
    project = ukraine_context["project"]
    registration = RegistrationFactory(
        project=project,
        source_id=registration_id,
        rdi_parser=UkraineRegistrationService,
    )

    amount_of_records = 4
    page_size = 2
    for _ in range(amount_of_records):
        record_factory(
            fields=fields,
            registration=registration.source_id,
            status=Record.STATUS_TO_IMPORT,
            files=files,
        )

    result = run_automate_rdi_creation_task(
        registration_id=registration.source_id,
        page_size=page_size,
        template="{business_area_name} template {date} {records}",
    )

    assert RegistrationDataImport.objects.count() == amount_of_records // page_size
    assert PendingIndividual.objects.count() == amount_of_records * expected_individuals_per_record
    assert result[0][0].startswith("ukraine")
    assert result[0][1] == page_size
    assert result[1][1] == page_size


def test_with_different_registration_ids_sri_lanka(
    record_factory: Callable[..., Record],
    run_automate_rdi_creation_task: Callable[..., list],
) -> None:
    business_area = BusinessAreaFactory(name="Sri Lanka")
    CountryFactory(name="Sri Lanka", short_name="Sri Lanka", iso_code2="LK", iso_code3="LKA", iso_num="0144")
    for doc_type in (
        IDENTIFICATION_TYPE_NATIONAL_ID,
        IDENTIFICATION_TYPE_BIRTH_CERTIFICATE,
        IDENTIFICATION_TYPE_BANK_STATEMENT,
    ):
        DocumentTypeFactory(key=IDENTIFICATION_TYPE_TO_KEY_MAPPING[doc_type], label=str(doc_type))
    admin1 = AreaFactory(p_code="LK1", name="LK Admin1")
    admin2 = AreaFactory(p_code="LK11", name="LK Admin2", parent=admin1)
    admin3 = AreaFactory(p_code="LK1163", name="LK Admin3", parent=admin2)
    AreaFactory(p_code="LK1163020", name="LK Admin4", parent=admin3)
    organization = OrganizationFactory(name=business_area.name, slug=business_area.slug, business_area=business_area)
    program = ProgramFactory(status=Program.ACTIVE, business_area=business_area)
    project = ProjectFactory(organization=organization, programme=program)
    registration = RegistrationFactory(
        project=project,
        source_id=17,
        rdi_parser=SriLankaRegistrationService,
    )

    amount_of_records = 4
    page_size = 2
    for _ in range(amount_of_records):
        record_factory(
            fields=SRI_LANKA_FIELDS,
            registration=registration.source_id,
            status=Record.STATUS_TO_IMPORT,
        )

    result = run_automate_rdi_creation_task(
        registration_id=registration.source_id,
        page_size=page_size,
        template="{business_area_name} template {date} {records}",
    )

    assert RegistrationDataImport.objects.count() == amount_of_records // page_size
    assert PendingIndividual.objects.count() == amount_of_records * 2
    assert result[0][0].startswith("Sri Lanka")
    assert result[0][1] == page_size
    assert result[1][1] == page_size


@pytest.mark.parametrize("registration_id", [999, 18, 19])
def test_with_different_registration_ids_not_implemented(
    registration_id: int, run_automate_rdi_creation_task: Callable[..., list]
) -> None:
    with pytest.raises(NotImplementedError):
        run_automate_rdi_creation_task(
            registration_id=registration_id,
            page_size=5,
            template="{business_area_name} template {date} {records}",
        )


def test_some_records_invalid(ukraine_context: dict[str, object], record_factory: Callable[..., Record]) -> None:
    registration = ukraine_context["registration"]
    record_ok = record_factory(
        fields=UKRAINE_FIELDS,
        registration=registration.source_id,
        status=Record.STATUS_TO_IMPORT,
    )
    record_error = record_factory(
        fields={"household": [{"aa": "bbb"}], "individuals": [{"abc": "xyz"}]},
        registration=registration.source_id,
        status=Record.STATUS_TO_IMPORT,
    )
    records_ids = [record_ok.id, record_error.id]

    rdi = UkraineBaseRegistrationService(registration).create_rdi(None, "ukraine rdi timezone UTC")

    assert Record.objects.count() == 2
    assert RegistrationDataImport.objects.filter(status=RegistrationDataImport.IMPORTING).count() == 1
    assert PendingIndividual.objects.count() == 0
    assert PendingHousehold.objects.count() == 0

    process_flex_records_task(registration.pk, rdi.pk, list(records_ids))
    rdi.refresh_from_db()
    record_ok.refresh_from_db()
    record_error.refresh_from_db()
    assert record_ok.status == Record.STATUS_IMPORTED
    assert record_error.status == Record.STATUS_ERROR
    assert rdi.status == RegistrationDataImport.DEDUPLICATION
    assert rdi.number_of_individuals == 1
    assert rdi.number_of_households == 1
    assert PendingIndividual.objects.count() == 1
    assert PendingHousehold.objects.count() == 1


def test_all_records_invalid(ukraine_context: dict[str, object], record_factory: Callable[..., Record]) -> None:
    registration = ukraine_context["registration"]
    record_error1 = record_factory(
        fields={"household": [{"aa": "bbb"}], "individuals": [{"abc": "xyz"}]},
        registration=registration.source_id,
        status=Record.STATUS_TO_IMPORT,
    )
    record_error2 = record_factory(
        fields={"household": [{"aa": "bbb"}], "individuals": [{"abc": "xyz"}]},
        registration=registration.source_id,
        status=Record.STATUS_TO_IMPORT,
    )
    records_ids = [record_error1.id, record_error2.id]

    rdi = UkraineBaseRegistrationService(registration).create_rdi(None, "ukraine rdi timezone UTC")

    assert Record.objects.count() == 2
    assert RegistrationDataImport.objects.filter(status=RegistrationDataImport.IMPORTING).count() == 1
    assert PendingIndividual.objects.count() == 0
    assert PendingHousehold.objects.count() == 0

    process_flex_records_task(registration.pk, rdi.pk, list(records_ids))
    rdi.refresh_from_db()
    record_error1.refresh_from_db()
    record_error2.refresh_from_db()
    assert record_error1.status == Record.STATUS_ERROR
    assert record_error2.status == Record.STATUS_ERROR
    assert rdi.status == RegistrationDataImport.IMPORT_ERROR
    assert rdi.error_message == "All Records failed validation during processing"
    assert rdi.number_of_individuals == 0
    assert rdi.number_of_households == 0
    assert PendingIndividual.objects.count() == 0
    assert PendingHousehold.objects.count() == 0


def test_ukraine_new_registration_form(
    ukraine_context: dict[str, object], record_factory: Callable[..., Record]
) -> None:
    registration = ukraine_context["registration"]
    record_factory(
        fields=UKRAINE_NEW_FORM_FIELDS,
        registration=registration.source_id,
        status=Record.STATUS_TO_IMPORT,
        files=UKRAINE_NEW_FORM_FILES,
    )

    records_ids = Record.objects.all().values_list("id", flat=True)
    registration.rdi_parser = UkraineRegistrationService
    registration.save()
    rdi = UkraineRegistrationService(registration).create_rdi(None, "ukraine rdi timezone UTC")

    assert Record.objects.count() == 1
    assert PendingIndividual.objects.count() == 0
    assert PendingHousehold.objects.count() == 0

    process_flex_records_task(
        registration.id,
        rdi.pk,
        list(records_ids),
    )
    rdi.refresh_from_db()

    assert Record.objects.filter(status=Record.STATUS_IMPORTED).count() == 1
    assert rdi.number_of_individuals == 2
    assert rdi.number_of_households == 1
    assert PendingIndividual.objects.count() == 2
    assert PendingHousehold.objects.count() == 1

    hh = PendingHousehold.objects.first()
    ind_1 = PendingIndividual.objects.filter(full_name="Pavlo Viktorovich Mok").first()
    ind_2 = PendingIndividual.objects.filter(full_name="Stefania Petrovich Bandera").first()
    doc_ind_1 = PendingDocument.objects.filter(individual=ind_1).first()
    doc_ind_2 = PendingDocument.objects.filter(individual=ind_2).first()

    assert hh.head_of_household == ind_1
    assert hh.admin1.p_code == "UA14"
    assert hh.admin2.p_code == "UA1408"
    assert hh.admin3 is None
    assert hh.enumerator_rec_id == 655384

    assert ind_1.birth_date == datetime.date(1990, 11, 11)
    assert ind_1.disability == NOT_DISABLED
    assert ind_1.phone_no == "+380952025248"
    assert ind_1.relationship == HEAD
    assert ind_1.sex == MALE

    assert ind_2.birth_date == datetime.date(2023, 3, 6)
    assert ind_2.sex == FEMALE
    assert ind_2.relationship == SON_DAUGHTER
    assert ind_2.disability == DISABLED

    assert doc_ind_1.document_number == "123465432321321"
    assert doc_ind_1.type.key == IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_TAX_ID]
    assert doc_ind_2.document_number == "I-ASD-454511"
    assert doc_ind_2.type.key == IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_BIRTH_CERTIFICATE]


def test_create_task_for_processing_records_not_implemented_error() -> None:
    with pytest.raises(NotImplementedError):
        create_task_for_processing_records(ServiceWithoutCeleryTask, uuid.uuid4(), uuid.uuid4(), [1])
