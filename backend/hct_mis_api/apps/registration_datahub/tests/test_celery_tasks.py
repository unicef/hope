import base64
from django.utils import timezone
import json
from contextlib import contextmanager
from pathlib import Path
from unittest.mock import Mock, patch

from django.conf import settings
from django.test import TestCase

from django_countries.fields import Country

from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.registration_data.models import RegistrationDataImport
from hct_mis_api.apps.registration_datahub.celery_tasks import (
    automate_rdi_creation_task,
)
from hct_mis_api.apps.registration_datahub.models import (
    ImportedDocumentType,
    ImportedIndividual,
    Record,
)
from hct_mis_api.apps.registration_datahub.services.flex_registration_service import (
    FlexRegistrationService,
)


def create_record(registration, status):
    # based on backend/hct_mis_api/apps/registration_datahub/tests/test_extract_records.py
    content = Path(f"{settings.PROJECT_ROOT}/apps/registration_datahub/tests/test_file/image.jpeg").read_bytes()
    fields = {
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
    files = {
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


def create_imported_document_types(country_code):
    for document_type_string, _ in FlexRegistrationService.DOCUMENT_MAPPING_TYPE_DICT.items():
        ImportedDocumentType.objects.create(country=Country(code=country_code), type=document_type_string)


def create_ukraine_business_area():
    BusinessArea.objects.create(
        slug="ukraine",
        code="1234",
        name="Ukraine",
        long_name="the long name of ukraine",
        region_code="3245",
        region_name="UA",
        has_data_sharing_agreement=True,
    )


def run_automate_rdi_creation_task(*args, **kwargs):
    @contextmanager
    def do_nothing_cache(*_args, **_kwargs):
        yield Mock()

    with patch(
        "hct_mis_api.apps.registration_datahub.celery_tasks.locked_cache",
        do_nothing_cache,
    ):
        return automate_rdi_creation_task(*args, **kwargs)


class TestAutomatingRDICreationTask(TestCase):
    databases = [
        "default",
        "cash_assist_datahub_ca",
        "cash_assist_datahub_erp",
        "cash_assist_datahub_mis",
        "registration_datahub",
    ]

    def test_successful_run_without_records_to_import(self):
        result = run_automate_rdi_creation_task(registration_id=123, page_size=1)
        assert result[0] == "No Records found"

    def test_not_running_with_record_status_not_to_import(self):
        create_ukraine_business_area()
        create_imported_document_types(country_code="UA")
        record = create_record(registration=234, status=Record.STATUS_ERROR)

        page_size = 1
        assert RegistrationDataImport.objects.count() == 0
        assert ImportedIndividual.objects.count() == 0
        result = run_automate_rdi_creation_task(registration_id=record.registration, page_size=page_size)
        assert RegistrationDataImport.objects.count() == 0
        assert ImportedIndividual.objects.count() == 0
        assert result[0] == "No Records found"

    def test_successful_run_with_records_to_import(self):
        create_ukraine_business_area()
        create_imported_document_types(country_code="UA")

        registration = 345
        amount_of_records = 10
        page_size = 3

        for _ in range(amount_of_records):
            create_record(registration=registration, status=Record.STATUS_TO_IMPORT)

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

    def test_successful_run_and_automatic_merge(self):
        create_ukraine_business_area()
        create_imported_document_types(country_code="UA")

        registration = 345
        amount_of_records = 10
        page_size = 3

        for _ in range(amount_of_records):
            create_record(registration=registration, status=Record.STATUS_TO_IMPORT)

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

    def test_successful_run_and_fix_task_id(self):
        create_ukraine_business_area()
        create_imported_document_types(country_code="UA")

        registration = 345
        amount_of_records = 10
        page_size = 3

        for _ in range(amount_of_records):
            create_record(registration=registration, status=Record.STATUS_TO_IMPORT)

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
