from io import BytesIO
from pathlib import Path
from unittest import mock

from django.conf import settings
from django.core.files import File
from django.test import TestCase

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.household.celery_tasks import (
    update_individuals_iban_from_xlsx_task,
)
from hct_mis_api.apps.household.fixtures import (
    BankAccountInfoFactory,
    RegistrationDataImportFactory,
    create_household_and_individuals,
)
from hct_mis_api.apps.household.models import (
    FEMALE,
    HEAD,
    MALE,
    WIFE_HUSBAND,
    XlsxUpdateFile,
)


def valid_file():
    content = Path(f"{settings.PROJECT_ROOT}/apps/household/tests/test_file/iban_update_valid.xlsx").read_bytes()
    return File(BytesIO(content), name="iban_update_valid.xlsx")


def invalid_file_no_match():
    content = Path(
        f"{settings.PROJECT_ROOT}/apps/household/tests/test_file/iban_update_invalid_no_match.xlsx"
    ).read_bytes()
    return File(BytesIO(content), name="iban_update_invalid_no_match.xlsx")


def invalid_file_empty_cell():
    content = Path(
        f"{settings.PROJECT_ROOT}/apps/household/tests/test_file/iban_update_invalid_empty_cell.xlsx"
    ).read_bytes()
    return File(BytesIO(content), name="iban_update_invalid_empty_cell.xlsx")


def invalid_file_bad_columns():
    content = Path(
        f"{settings.PROJECT_ROOT}/apps/household/tests/test_file/iban_update_invalid_bad_columns.xlsx"
    ).read_bytes()
    return File(BytesIO(content), name="iban_update_invalid_bad_columns.xlsx")


def invalid_file():
    content = Path(f"{settings.PROJECT_ROOT}/apps/household/tests/test_file/iban_update_invalid_file.xlsx").read_bytes()
    return File(BytesIO(content), name="iban_update_invalid_file.xlsx")


class TestIndividualXlsxUpdate(TestCase):
    databases = "__all__"

    @classmethod
    def setUpTestData(cls):
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

    @mock.patch(
        "hct_mis_api.apps.household.services.individuals_iban_xlsx_update.IndividualsIBANXlsxUpdate._prepare_email"
    )
    def test_update_individuals_iban_from_xlsx_task_invalid_file_error(self, prepare_email_mock):
        update_individuals_iban_from_xlsx_task.run(
            xlsx_update_file_id=self.xlsx_invalid_file.id,
            uploaded_by_id=self.user.id,
        )
        prepare_email_mock.assert_called_once_with(
            context={
                "first_name": self.user.first_name,
                "last_name": self.user.last_name,
                "email": self.user.email,
                "message": "There was an unexpected error during Individuals IBAN update: 'Worksheet Individuals does not exist.'",
                "upload_file_id": str(self.xlsx_invalid_file.id),
            }
        )

    @mock.patch(
        "hct_mis_api.apps.household.services.individuals_iban_xlsx_update.IndividualsIBANXlsxUpdate._prepare_email"
    )
    def test_update_individuals_iban_from_xlsx_task_invalid_file_bad_columns_fail(self, prepare_email_mock):
        update_individuals_iban_from_xlsx_task.run(
            xlsx_update_file_id=self.xlsx_invalid_file_bad_columns.id,
            uploaded_by_id=self.user.id,
        )
        prepare_email_mock.assert_called_once_with(
            context={
                "first_name": self.user.first_name,
                "last_name": self.user.last_name,
                "email": self.user.email,
                "message": "['No UNICEF_ID column in provided file', 'No IBAN column in provided file', 'No BANK_NAME column in provided file']",
                "upload_file_id": str(self.xlsx_invalid_file_bad_columns.id),
            }
        )

    @mock.patch(
        "hct_mis_api.apps.household.services.individuals_iban_xlsx_update.IndividualsIBANXlsxUpdate._prepare_email"
    )
    def test_update_individuals_iban_from_xlsx_task_invalid_no_match_fail(self, prepare_email_mock):
        update_individuals_iban_from_xlsx_task.run(
            xlsx_update_file_id=self.xlsx_invalid_file_no_match.id,
            uploaded_by_id=self.user.id,
        )
        prepare_email_mock.assert_called_once_with(
            context={
                "first_name": self.user.first_name,
                "last_name": self.user.last_name,
                "email": self.user.email,
                "message": "['No matching Individuals for rows: [2, 3]']",
                "upload_file_id": str(self.xlsx_invalid_file_no_match.id),
            }
        )

    @mock.patch(
        "hct_mis_api.apps.household.services.individuals_iban_xlsx_update.IndividualsIBANXlsxUpdate._prepare_email"
    )
    def test_update_individuals_iban_from_xlsx_task_valid_match(self, prepare_email_mock):
        # creating BankAccountInfo for only one individual, second one should be populated on demand
        BankAccountInfoFactory(individual=self.individuals[0])
        self.individuals[0].save()

        update_individuals_iban_from_xlsx_task.run(
            xlsx_update_file_id=self.xlsx_valid_file.id,
            uploaded_by_id=self.user.id,
        )

        prepare_email_mock.assert_called_once_with(
            context={
                "first_name": self.user.first_name,
                "last_name": self.user.last_name,
                "email": self.user.email,
                "message": "All of the Individuals IBAN number we're updated successfully",
                "upload_file_id": str(self.xlsx_valid_file.id),
            }
        )
        bank_account_info_0 = self.individuals[0].bank_account_info.first()
        bank_account_info_1 = self.individuals[1].bank_account_info.first()
        self.assertEqual(bank_account_info_0.bank_account_number, "1111111111")
        self.assertEqual(bank_account_info_0.bank_name, "Super Bank")
        self.assertEqual(bank_account_info_1.bank_account_number, "2222222222")
        self.assertEqual(bank_account_info_1.bank_name, "Bank")

    @mock.patch(
        "hct_mis_api.apps.household.services.individuals_iban_xlsx_update.IndividualsIBANXlsxUpdate._prepare_email"
    )
    def test_update_individuals_iban_from_xlsx_task_invalid_empty_cell(self, prepare_email_mock):
        update_individuals_iban_from_xlsx_task.run(
            xlsx_update_file_id=self.xlsx_invalid_file_empty_cell.id,
            uploaded_by_id=self.user.id,
        )
        prepare_email_mock.assert_called_once_with(
            context={
                "first_name": self.user.first_name,
                "last_name": self.user.last_name,
                "email": self.user.email,
                "message": "There was an unexpected error during Individuals IBAN update: BankAccountInfo data is missing for Individual IND-88-0000.0002 in Row 3, One of IBAN/BANK_NAME value was not provided. Please validate also other rows for missing data.",
                "upload_file_id": str(self.xlsx_invalid_file_empty_cell.id),
            }
        )
