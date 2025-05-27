import json
from io import BytesIO
from pathlib import Path
from typing import Any
from unittest import mock

from constance.test import override_config
from django.conf import settings
from django.core.files import File
from django.template.loader import render_to_string
from django.test import TestCase, override_settings

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.household.celery_tasks import \
    update_individuals_iban_from_xlsx_task
from hct_mis_api.apps.household.fixtures import (
    BankAccountInfoFactory, RegistrationDataImportFactory,
    create_household_and_individuals)
from hct_mis_api.apps.household.models import (FEMALE, HEAD, MALE,
                                               WIFE_HUSBAND, XlsxUpdateFile)


def valid_file() -> File:
    content = Path(f"{settings.TESTS_ROOT}/apps/household/test_file/iban_update_valid.xlsx").read_bytes()
    return File(BytesIO(content), name="iban_update_valid.xlsx")


def invalid_file_no_match() -> File:
    content = Path(f"{settings.TESTS_ROOT}/apps/household/test_file/iban_update_invalid_no_match.xlsx").read_bytes()
    return File(BytesIO(content), name="iban_update_invalid_no_match.xlsx")


def invalid_file_empty_cell() -> File:
    content = Path(f"{settings.TESTS_ROOT}/apps/household/test_file/iban_update_invalid_empty_cell.xlsx").read_bytes()
    return File(BytesIO(content), name="iban_update_invalid_empty_cell.xlsx")


def invalid_file_bad_columns() -> File:
    content = Path(f"{settings.TESTS_ROOT}/apps/household/test_file/iban_update_invalid_bad_columns.xlsx").read_bytes()
    return File(BytesIO(content), name="iban_update_invalid_bad_columns.xlsx")


def invalid_file() -> File:
    content = Path(f"{settings.TESTS_ROOT}/apps/household/test_file/iban_update_invalid_file.xlsx").read_bytes()
    return File(BytesIO(content), name="iban_update_invalid_file.xlsx")


class TestIndividualXlsxUpdate(TestCase):
    databases = "__all__"

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        create_afghanistan()
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")
        registration_data_import = RegistrationDataImportFactory(business_area=cls.business_area)

        cls.user = UserFactory(email="test@example.com")

        cls.xlsx_valid_file = XlsxUpdateFile.objects.create(
            file=valid_file(), business_area=cls.business_area, uploaded_by=cls.user
        )

        cls.xlsx_invalid_file_no_match = XlsxUpdateFile.objects.create(
            file=invalid_file_no_match(), business_area=cls.business_area, uploaded_by=cls.user
        )

        cls.xlsx_invalid_file_empty_cell = XlsxUpdateFile.objects.create(
            file=invalid_file_empty_cell(), business_area=cls.business_area, uploaded_by=cls.user
        )

        cls.xlsx_invalid_file_bad_columns = XlsxUpdateFile.objects.create(
            file=invalid_file_bad_columns(), business_area=cls.business_area, uploaded_by=cls.user
        )

        cls.xlsx_invalid_file = XlsxUpdateFile.objects.create(
            file=invalid_file(), business_area=cls.business_area, uploaded_by=cls.user
        )

        household_data = {
            "registration_data_import": registration_data_import,
            "business_area": cls.business_area,
        }
        individuals_data = [
            {
                "registration_data_import": registration_data_import,
                "given_name": "Patryk",
                "full_name": "Patryk Kowalski",
                "middle_name": "",
                "family_name": "Kowalski",
                "phone_no": "123-123-123",
                "phone_no_alternative": "",
                "relationship": HEAD,
                "sex": MALE,
                "birth_date": "1955-09-07",
                "unicef_id": "IND-88-0000.0005",
            },
            {
                "registration_data_import": registration_data_import,
                "given_name": "Karolina",
                "full_name": "Karolina Kowalska",
                "middle_name": "",
                "family_name": "Kowalska",
                "phone_no": "453-85-423",
                "phone_no_alternative": "",
                "relationship": WIFE_HUSBAND,
                "sex": FEMALE,
                "birth_date": "1955-09-05",
                "unicef_id": "IND-88-0000.0002",
            },
        ]
        _, cls.individuals = create_household_and_individuals(
            household_data=household_data, individuals_data=individuals_data
        )
        # overwrite unicef_id
        for individual in cls.individuals:
            individual.save()

    @mock.patch("hct_mis_api.apps.utils.celery_tasks.requests.post")
    @override_settings(EMAIL_SUBJECT_PREFIX="test")
    @override_config(ENABLE_MAILJET=True)
    def test_update_individuals_iban_from_xlsx_task_invalid_file_error(self, mocked_requests_post: Any) -> None:
        update_individuals_iban_from_xlsx_task.run(
            xlsx_update_file_id=self.xlsx_invalid_file.id,
            uploaded_by_id=self.user.id,
        )

        context = {
            "first_name": self.user.first_name,
            "last_name": self.user.last_name,
            "email": self.user.email,
            "message": "There was an unexpected error during Individuals IBAN update: 'Worksheet Individuals does not exist.'",
            "upload_file_id": str(self.xlsx_invalid_file.id),
        }

        expected_data = self._get_expected_email_body(context)

        mocked_requests_post.assert_called_once_with(
            "https://api.mailjet.com/v3.1/send",
            auth=(settings.MAILJET_API_KEY, settings.MAILJET_SECRET_KEY),
            data=expected_data,
        )

    @mock.patch("hct_mis_api.apps.utils.celery_tasks.requests.post")
    @override_settings(EMAIL_SUBJECT_PREFIX="test")
    @override_config(ENABLE_MAILJET=True)
    def test_update_individuals_iban_from_xlsx_task_invalid_file_bad_columns_fail(
        self, mocked_requests_post: Any
    ) -> None:
        update_individuals_iban_from_xlsx_task.run(
            xlsx_update_file_id=self.xlsx_invalid_file_bad_columns.id,
            uploaded_by_id=self.user.id,
        )
        context = {
            "first_name": self.user.first_name,
            "last_name": self.user.last_name,
            "email": self.user.email,
            "message": "['No UNICEF_ID column in provided file', 'No IBAN column in provided file', 'No BANK_NAME column in provided file']",
            "upload_file_id": str(self.xlsx_invalid_file_bad_columns.id),
        }
        expected_data = self._get_expected_email_body(context)

        mocked_requests_post.assert_called_once_with(
            "https://api.mailjet.com/v3.1/send",
            auth=(settings.MAILJET_API_KEY, settings.MAILJET_SECRET_KEY),
            data=expected_data,
        )

    @mock.patch("hct_mis_api.apps.utils.celery_tasks.requests.post")
    @override_settings(EMAIL_SUBJECT_PREFIX="test")
    @override_config(ENABLE_MAILJET=True)
    def test_update_individuals_iban_from_xlsx_task_invalid_no_match_fail(self, mocked_requests_post: Any) -> None:
        update_individuals_iban_from_xlsx_task.run(
            xlsx_update_file_id=self.xlsx_invalid_file_no_match.id,
            uploaded_by_id=self.user.id,
        )
        context = {
            "first_name": self.user.first_name,
            "last_name": self.user.last_name,
            "email": self.user.email,
            "message": "['No matching Individuals for rows: [2, 3]']",
            "upload_file_id": str(self.xlsx_invalid_file_no_match.id),
        }
        expected_data = self._get_expected_email_body(context)
        mocked_requests_post.assert_called_once_with(
            "https://api.mailjet.com/v3.1/send",
            auth=(settings.MAILJET_API_KEY, settings.MAILJET_SECRET_KEY),
            data=expected_data,
        )

    @mock.patch("hct_mis_api.apps.utils.celery_tasks.requests.post")
    @override_settings(EMAIL_SUBJECT_PREFIX="test")
    @override_config(ENABLE_MAILJET=True)
    def test_update_individuals_iban_from_xlsx_task_valid_match(self, mocked_requests_post: Any) -> None:
        # creating BankAccountInfo for only one individual, second one should be populated on demand
        BankAccountInfoFactory(individual=self.individuals[0])
        self.individuals[0].save()

        update_individuals_iban_from_xlsx_task.run(
            xlsx_update_file_id=self.xlsx_valid_file.id,
            uploaded_by_id=self.user.id,
        )

        context = {
            "first_name": self.user.first_name,
            "last_name": self.user.last_name,
            "email": self.user.email,
            "message": "All of the Individuals IBAN number we're updated successfully",
            "upload_file_id": str(self.xlsx_valid_file.id),
        }
        expected_data = self._get_expected_email_body(context)
        mocked_requests_post.assert_called_once_with(
            "https://api.mailjet.com/v3.1/send",
            auth=(settings.MAILJET_API_KEY, settings.MAILJET_SECRET_KEY),
            data=expected_data,
        )

        bank_account_info_0 = self.individuals[0].bank_account_info.first()
        bank_account_info_1 = self.individuals[1].bank_account_info.first()
        self.assertEqual(bank_account_info_0.bank_account_number, "1111111111")
        self.assertEqual(bank_account_info_0.bank_name, "Super Bank")
        self.assertEqual(bank_account_info_1.bank_account_number, "2222222222")
        self.assertEqual(bank_account_info_1.bank_name, "Bank")

    @mock.patch("hct_mis_api.apps.utils.celery_tasks.requests.post")
    @override_settings(EMAIL_SUBJECT_PREFIX="test")
    @override_config(ENABLE_MAILJET=True)
    def test_update_individuals_iban_from_xlsx_task_invalid_empty_cell(self, mocked_requests_post: Any) -> None:
        update_individuals_iban_from_xlsx_task.run(
            xlsx_update_file_id=self.xlsx_invalid_file_empty_cell.id,
            uploaded_by_id=self.user.id,
        )
        context = {
            "first_name": self.user.first_name,
            "last_name": self.user.last_name,
            "email": self.user.email,
            "message": "There was an unexpected error during Individuals IBAN update: BankAccountInfo data is missing for Individual IND-88-0000.0002 in Row 3, One of IBAN/BANK_NAME value was not provided. Please validate also other rows for missing data.",
            "upload_file_id": str(self.xlsx_invalid_file_empty_cell.id),
        }
        expected_data = self._get_expected_email_body(context)
        mocked_requests_post.assert_called_once_with(
            "https://api.mailjet.com/v3.1/send",
            auth=(settings.MAILJET_API_KEY, settings.MAILJET_SECRET_KEY),
            data=expected_data,
        )

    def _get_expected_email_body(self, context: dict) -> str:
        return json.dumps(
            {
                "Messages": [
                    {
                        "From": {"Email": settings.DEFAULT_EMAIL, "Name": settings.DEFAULT_EMAIL_DISPLAY},
                        "Subject": f"[test] Individual IBANs xlsx [{context['upload_file_id']}] update result",
                        "To": [
                            {
                                "Email": "test@example.com",
                            },
                        ],
                        "Cc": [],
                        "HTMLPart": render_to_string(
                            "admin/household/individual/individuals_iban_xlsx_update_email.txt",
                            context=context,
                        ),
                        "TextPart": render_to_string(
                            "admin/household/individual/individuals_iban_xlsx_update_email.txt",
                            context=context,
                        ),
                    }
                ]
            }
        )
