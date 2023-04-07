import base64
import datetime
import json
import uuid
from abc import ABC
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, Generator, Optional
from unittest.mock import Mock, patch

from django.conf import settings
from django.test import TestCase
from django.utils import timezone

from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.household.models import (
    DISABLED,
    FEMALE,
    HEAD,
    IDENTIFICATION_TYPE_BIRTH_CERTIFICATE,
    IDENTIFICATION_TYPE_TAX_ID,
    MALE,
    NOT_DISABLED,
    SON_DAUGHTER,
)
from hct_mis_api.apps.registration_data.models import RegistrationDataImport
from hct_mis_api.apps.registration_datahub.celery_tasks import (
    automate_rdi_creation_task,
    process_flex_records_task,
)
from hct_mis_api.apps.registration_datahub.models import (
    ImportedBankAccountInfo,
    ImportedDocument,
    ImportedDocumentType,
    ImportedHousehold,
    ImportedIndividual,
    Record,
)
from hct_mis_api.apps.registration_datahub.services.base_flex_registration_service import (
    BaseRegistrationService,
)
from hct_mis_api.apps.registration_datahub.services.flex_registration_service import (
    create_task_for_processing_records,
)
from hct_mis_api.apps.registration_datahub.services.ukraine_flex_registration_service import (
    UkraineBaseRegistrationService,
    UkraineRegistrationService,
)

SRI_LANKA_FIELDS: Dict = {
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
            "account_number": "179200100062564",
            "bank_description": "People's Bank",
            "bank_name": "7135",
            "branch_or_branch_code": "7135_179",
            "confirm_bank_account_number": "179200100062564",
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

UKRAINE_FIELDS: Dict = {
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
            "given_name_i_c": "\u041d\u0430\u0442\u0430\u043b\u0456\u044f",
            "family_name_i_c": "\u0421\u0430\u043f\u0456\u0433\u0430",
            "patronymic": "\u0410\u0434\u0430\u043c\u0456\u0432\u043d\u0430",
            "birth_date": "1983-09-24",
            "gender_i_c": "female",
            "relationship_i_c": "head",
            "disability_i_c": "y",
            "disabiliyt_recognize_i_c": "y",
            "phone_no_i_c": "0636060474",
            "q1": "",
            "tax_id_no_i_c": "123123123",
            "national_id_no_i_c_1": "",
            "international_passport_i_c": "",
            "drivers_license_no_i_c": "",
            "birth_certificate_no_i_c": "",
            "residence_permit_no_i_c": "",
            "role_i_c": "y",
            "bank_account_h_f": "y",
            "bank_name_h_f": "privatbank",
            "other_bank_name": "",
            "bank_account": 2356789789789789,
            "bank_account_number": "879789789",
            "debit_card_number_h_f": 9978967867666,
            "debit_card_number": "87987979789789",
        }
    ],
}

UKRAINE_NEW_FORM_FIELDS: Dict = {
    "ip": "176.113.164.17",
    "counters": {
        "start": "Thu Mar 23 2023 14:26:07 GMT+0200 (Eastern European Standard Time)",
        "total": "71464926",
        "rounds": "1",
        "elapsed": "71464926",
    },
    "household": [{"admin1_h_c": "UA14", "admin2_h_c": "UA1408", "admin3_h_c": "UA1408005"}],
    "marketing": [{"can_unicef_contact_you": [{}]}],
    "individuals": [
        {
            "id_type": "tax_id",
            "role_i_c": "y",
            "birth_date": "1990-11-11",
            "gender_i_c": "male",
            "patronymic": "Viktorovich",
            "bank_account": "IBAN 1236 5498 7999 8999",
            "phone_no_i_c": "+380952025248",
            "tax_id_no_i_c": "123465432321321",
            "disability_i_c": "n",
            "given_name_i_c": "Pavlo",
            "family_name_i_c": "Mok",
            "bank_account_h_f": "y",
            "bank_name_h_f": "AvalBank",  # TODO: required field should be in reg form ??
            "relationship_i_c": "head",
            "bank_account_number": "1236 5498 7999 1999",
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
            "birth_certificate_no_i_c": "І-ASD-454511",
        },
    ],
    "validator_uk": [{"validation": "y"}],
}

UKRAINE_NEW_FORM_FILES: Dict = {
    "individuals": [
        {},  # no files for first Individual
        {
            "disability_certificate_picture": str(base64.b64encode(b"h\x65llo"), "utf-8"),
            "birth_certificate_picture": str(base64.b64encode(b"h\x65llo"), "utf-8"),
        },
    ],
}


def create_record(fields: Dict, registration: int, status: str, files: Optional[Dict] = None) -> Record:
    # based on backend/hct_mis_api/apps/registration_datahub/tests/test_extract_records.py
    content = Path(f"{settings.PROJECT_ROOT}/apps/registration_datahub/tests/test_file/image.jpeg").read_bytes()

    # need files for each Individual
    files = files or {
        "individuals": [
            {
                "disability_certificate_picture": str(base64.b64encode(content), "utf-8"),
                "birth_certificate_picture": str(base64.b64encode(content), "utf-8"),
            }
        ],
    }

    return Record.objects.create(
        registration=registration,
        status=status,
        timestamp=timezone.now(),
        data=None,
        source_id=1,
        fields=fields,
        files=json.dumps(files).encode(),
    )


def create_imported_document_types() -> None:
    for document_type_string, _ in UkraineBaseRegistrationService.DOCUMENT_MAPPING_TYPE_DICT.items():
        ImportedDocumentType.objects.create(type=document_type_string)


def create_ukraine_business_area() -> None:
    BusinessArea.objects.create(
        slug="ukraine",
        code="1234",
        name="Ukraine",
        long_name="the long name of ukraine",
        region_code="3245",
        region_name="UA",
        has_data_sharing_agreement=True,
    )


def create_sri_lanka_business_area() -> None:
    BusinessArea.objects.create(
        slug="sri-lanka",
        code="0608",
        name="Sri Lanka",
        long_name="THE DEMOCRATIC SOCIALIST REPUBLIC OF SRI LANKA",
        region_code="64",
        region_name="SAR",
        has_data_sharing_agreement=True,
    )


def create_czech_republic_business_area() -> None:
    BusinessArea.objects.create(
        slug="czech-republic",
        code="BOCZ",
        name="Czech Republic",
        long_name="The Czech Republic",
        region_code="66",
        region_name="ECAR",
        has_data_sharing_agreement=True,
    )


def run_automate_rdi_creation_task(*args: Any, **kwargs: Any) -> Any:
    @contextmanager
    def do_nothing_cache(*_args: Any, **_kwargs: Any) -> Generator:
        yield Mock()

    with patch(
        "hct_mis_api.apps.registration_datahub.celery_tasks.locked_cache",
        do_nothing_cache,
    ):
        return automate_rdi_creation_task(*args, **kwargs)


class TestAutomatingRDICreationTask(TestCase):
    databases = {
        "default",
        "cash_assist_datahub_ca",
        "cash_assist_datahub_erp",
        "cash_assist_datahub_mis",
        "registration_datahub",
    }
    fixtures = ("hct_mis_api/apps/geo/fixtures/data.json",)

    def test_successful_run_without_records_to_import(self) -> None:
        result = run_automate_rdi_creation_task(registration_id=2, page_size=1)
        assert result[0] == "No Records found"

    def test_not_running_with_record_status_not_to_import(self) -> None:
        create_ukraine_business_area()
        create_imported_document_types()
        record = create_record(fields=UKRAINE_FIELDS, registration=2, status=Record.STATUS_ERROR)

        page_size = 1
        assert RegistrationDataImport.objects.count() == 0
        assert ImportedIndividual.objects.count() == 0
        result = run_automate_rdi_creation_task(registration_id=record.registration, page_size=page_size)
        assert RegistrationDataImport.objects.count() == 0
        assert ImportedIndividual.objects.count() == 0
        assert result[0] == "No Records found"

    def test_successful_run_with_records_to_import(self) -> None:
        create_ukraine_business_area()
        create_imported_document_types()

        registration = 2
        amount_of_records = 10
        page_size = 3

        for _ in range(amount_of_records):
            create_record(fields=UKRAINE_FIELDS, registration=registration, status=Record.STATUS_TO_IMPORT)

        assert Record.objects.count() == amount_of_records
        assert RegistrationDataImport.objects.count() == 0
        assert ImportedIndividual.objects.count() == 0

        result = run_automate_rdi_creation_task(
            registration_id=registration, page_size=page_size, template="some template {date} {records}"
        )

        assert RegistrationDataImport.objects.count() == 4  # or math.ceil(amount_of_records / page_size)
        assert ImportedIndividual.objects.count() == amount_of_records
        assert result[0][0].startswith("some template")
        assert result[0][1] == page_size
        assert result[1][1] == page_size
        assert result[2][1] == page_size
        assert result[3][1] == amount_of_records - 3 * page_size

    def test_successful_run_and_automatic_merge(self) -> None:
        create_ukraine_business_area()
        create_imported_document_types()

        registration = 3
        amount_of_records = 10
        page_size = 3

        for _ in range(amount_of_records):
            create_record(fields=UKRAINE_FIELDS, registration=registration, status=Record.STATUS_TO_IMPORT)

        assert Record.objects.count() == amount_of_records
        assert RegistrationDataImport.objects.count() == 0
        assert ImportedIndividual.objects.count() == 0

        with patch(
            "hct_mis_api.apps.registration_datahub.celery_tasks.merge_registration_data_import_task.delay"
        ) as merge_task_mock:
            result = run_automate_rdi_creation_task(
                registration_id=registration,
                page_size=page_size,
                template="some template {date} {records}",
                auto_merge=True,
            )
            assert len(result) == 4
            assert merge_task_mock.called

    def test_successful_run_and_fix_task_id(self) -> None:
        create_ukraine_business_area()
        create_imported_document_types()

        registration = 2
        amount_of_records = 10
        page_size = 3

        for _ in range(amount_of_records):
            create_record(fields=UKRAINE_FIELDS, registration=registration, status=Record.STATUS_TO_IMPORT)

        assert Record.objects.count() == amount_of_records
        assert RegistrationDataImport.objects.count() == 0
        assert ImportedIndividual.objects.count() == 0

        with patch(
            "hct_mis_api.apps.registration_datahub.celery_tasks.merge_registration_data_import_task.delay"
        ) as merge_task_mock:
            result = run_automate_rdi_creation_task(
                registration_id=registration,
                page_size=page_size,
                template="some template {date} {records}",
                fix_tax_id=True,
            )
        assert len(result) == 4
        assert not merge_task_mock.called  # auto_merge was not set ; defaults to false
        assert set(Record.objects.values_list("unique_field", flat=True)) == {"123123123"}

    def test_with_different_registration_ids(self) -> None:
        """
        based on registration_id select RegistrationService
        Ukraine - 2, 3 -> UkraineBaseRegistrationService()
        Ukraine - 11 -> UkraineRegistrationService()
        Sri Lanka - 17 -> SriLankaRegistrationService()
        Czech Republic - 18, 19 -> NotImplementedError for now

        check get_registration_to_rdi_service_map()
        """
        create_ukraine_business_area()
        create_imported_document_types()
        create_czech_republic_business_area()
        create_sri_lanka_business_area()

        registration_id_to_ba_name_map = {
            2: "ukraine",
            3: "ukraine",
            11: "ukraine", # new form
            17: "sri-lanka",
            18: "czech republic",
            19: "czech republic",
        }
        records_count = 0
        rdi_count = 0
        imported_ind_count = 0

        amount_of_records = 10
        page_size = 5

        registration_ids = [2, 3, 11, 17, 18, 19, 999]
        for registration_id in registration_ids:
            for _ in range(amount_of_records):
                records_count += 1
                files = None
                if registration_id == 17:
                    data = SRI_LANKA_FIELDS
                elif registration_id == 11:
                    data = UKRAINE_NEW_FORM_FIELDS
                    files = UKRAINE_NEW_FORM_FILES
                else:
                    data = UKRAINE_FIELDS
                create_record(fields=data, registration=registration_id, status=Record.STATUS_TO_IMPORT, files=files)

            assert Record.objects.count() == records_count
            assert RegistrationDataImport.objects.count() == rdi_count
            assert ImportedIndividual.objects.count() == imported_ind_count

            # NotImplementedError
            if registration_id in [999, 18, 19]:
                with self.assertRaises(NotImplementedError):
                    run_automate_rdi_creation_task(
                        registration_id=registration_id,
                        page_size=page_size,
                        template="{business_area_name} template {date} {records}",
                    )
            else:
                rdi_count += amount_of_records // page_size
                # for SriLanka we create "children" and "caretaker" as two separate Individuals
                # and for Ukr new form reg_id=11 we create 2 Ind and 1 Hh
                # that why need amount_of_records * 2
                imported_ind_count += amount_of_records if registration_id not in [17, 11] else amount_of_records * 2
                result = run_automate_rdi_creation_task(
                    registration_id=registration_id,
                    page_size=page_size,
                    template="{business_area_name} template {date} {records}",
                )

                assert RegistrationDataImport.objects.count() == rdi_count
                assert ImportedIndividual.objects.count() == imported_ind_count
                assert result[0][0].startswith(registration_id_to_ba_name_map.get(registration_id, "wrong"))
                assert result[0][1] == page_size
                assert result[1][1] == page_size

    def test_atomic_rollback_if_record_invalid(self) -> None:
        for document_type in UkraineBaseRegistrationService.DOCUMENT_MAPPING_TYPE_DICT.keys():
            ImportedDocumentType.objects.get_or_create(type=document_type, label="abc")
        create_ukraine_business_area()
        create_record(fields=UKRAINE_FIELDS, registration=2, status=Record.STATUS_TO_IMPORT)
        create_record(
            fields={"household": [{"aa": "bbb"}], "individuals": [{"abc": "xyz"}]},
            registration=3,
            status=Record.STATUS_TO_IMPORT,
        )
        records_ids = Record.objects.all().values_list("id", flat=True)
        rdi = UkraineBaseRegistrationService().create_rdi(None, "ukraine rdi timezone UTC")

        assert Record.objects.count() == 2
        assert RegistrationDataImport.objects.filter(status=RegistrationDataImport.IMPORTING).count() == 1
        assert ImportedIndividual.objects.count() == 0
        assert ImportedHousehold.objects.count() == 0

        process_flex_records_task(rdi.pk, list(records_ids), UkraineBaseRegistrationService.REGISTRATION_ID)
        rdi.refresh_from_db()

        assert Record.objects.filter(status=Record.STATUS_TO_IMPORT).count() == 1
        assert Record.objects.filter(status=Record.STATUS_ERROR).count() == 1

        assert RegistrationDataImport.objects.filter(status=RegistrationDataImport.IMPORT_ERROR).count() == 1
        assert rdi.error_message == "Records with errors were found during processing"
        assert rdi.number_of_individuals == 0
        assert rdi.number_of_households == 0
        assert ImportedIndividual.objects.count() == 0
        assert ImportedHousehold.objects.count() == 0

    def test_ukraine_new_registration_form(self) -> None:
        for document_type in UkraineRegistrationService.DOCUMENT_MAPPING_TYPE_DICT.keys():
            ImportedDocumentType.objects.get_or_create(type=document_type, label="abc")
        create_ukraine_business_area()
        create_record(
            fields=UKRAINE_NEW_FORM_FIELDS,
            registration=11,
            status=Record.STATUS_TO_IMPORT,
            files=UKRAINE_NEW_FORM_FILES,
        )
        records_ids = Record.objects.all().values_list("id", flat=True)
        rdi = UkraineRegistrationService().create_rdi(None, "ukraine rdi timezone UTC")

        assert Record.objects.count() == 1
        assert RegistrationDataImport.objects.filter(status=RegistrationDataImport.IMPORTING).count() == 1
        assert ImportedIndividual.objects.count() == 0
        assert ImportedHousehold.objects.count() == 0

        process_flex_records_task(rdi.pk, list(records_ids), UkraineRegistrationService.REGISTRATION_ID)
        rdi.refresh_from_db()

        assert Record.objects.filter(status=Record.STATUS_IMPORTED).count() == 1

        assert rdi.number_of_individuals == 2
        assert rdi.number_of_households == 1
        assert ImportedIndividual.objects.count() == 2
        assert ImportedHousehold.objects.count() == 1

        hh = ImportedHousehold.objects.first()
        ind_1 = ImportedIndividual.objects.filter(full_name="Pavlo Viktorovich Mok").first()
        ind_2 = ImportedIndividual.objects.filter(full_name="Stefania Petrovich Bandera").first()
        doc_ind_1 = ImportedDocument.objects.filter(individual=ind_1).first()
        doc_ind_2 = ImportedDocument.objects.filter(individual=ind_2).first()
        bank_acc_info = ImportedBankAccountInfo.objects.filter(individual=ind_1).first()

        assert hh.head_of_household == ind_1
        assert hh.admin1 == "UA14"
        assert hh.admin2 == "UA1408"
        assert hh.admin3 == "UA1408005"

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
        assert doc_ind_1.type.type == IDENTIFICATION_TYPE_TAX_ID
        assert doc_ind_2.document_number == "І-ASD-454511"
        assert doc_ind_2.type.type == IDENTIFICATION_TYPE_BIRTH_CERTIFICATE

        assert bank_acc_info.bank_account_number == "IBAN1236549879998999"
        assert bank_acc_info.debit_card_number == "1236549879991999"
        assert bank_acc_info.bank_name == "AvalBank"

    def test_create_task_for_processing_records_not_implemented_error(self) -> None:
        class ServiceWithoutCeleryTask(BaseRegistrationService, ABC):
            PROCESS_FLEX_RECORDS_TASK = None

        with self.assertRaises(NotImplementedError):
            create_task_for_processing_records(ServiceWithoutCeleryTask, uuid.uuid4(), [1])
