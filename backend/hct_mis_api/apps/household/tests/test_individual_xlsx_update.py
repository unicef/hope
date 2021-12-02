from io import BytesIO
from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.management import call_command

from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.household.fixtures import create_household_and_individuals
from hct_mis_api.apps.household.individual_xlsx_update import (
    IndividualXlsxUpdate,
    InvalidColumnsError,
)
from hct_mis_api.apps.household.models import (
    FEMALE,
    HEAD,
    MALE,
    SON_DAUGHTER,
    WIFE_HUSBAND,
    Individual,
    XlsxUpdateFile,
)
from hct_mis_api.apps.registration_data.fixtures import RegistrationDataImportFactory


def valid_file():
    content = Path(f"{settings.PROJECT_ROOT}/apps/household/tests/test_file/valid_updated_test_file.xlsx").read_bytes()
    return File(BytesIO(content), name="valid_updated_test_file.xlsx")


def invalid_file():
    content = Path(
        f"{settings.PROJECT_ROOT}/apps/household/tests/test_file/invalid_updated_test_file.xlsx"
    ).read_bytes()
    return File(BytesIO(content), name="invalid_updated_test_file.xlsx")


class TestIndividualXlsxUpdate(APITestCase):
    def setUp(self) -> None:
        call_command("loadbusinessareas")
        self.business_area = BusinessArea.objects.get(slug="afghanistan")

        registration_data_import = RegistrationDataImportFactory(business_area=self.business_area)
        self.xlsx_update_file = XlsxUpdateFile.objects.create(
            file=valid_file(),
            business_area=self.business_area,
            xlsx_match_columns=["individual__given_name"],
        )

        self.xlsx_update_invalid_file = XlsxUpdateFile.objects.create(
            file=invalid_file(),
            business_area=self.business_area,
            xlsx_match_columns=["individual__given_name"],
        )

        household_data = {
            "registration_data_import": registration_data_import,
            "business_area": self.business_area,
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
            },
            {
                "registration_data_import": registration_data_import,
                "given_name": "Angela",
                "full_name": "Angela Kowalska",
                "middle_name": "",
                "family_name": "Kowalska",
                "phone_no": "934-25-25-121",
                "phone_no_alternative": "",
                "relationship": SON_DAUGHTER,
                "sex": FEMALE,
                "birth_date": "1985-08-12",
            },
            {
                "registration_data_import": registration_data_import,
                "given_name": "Angela",
                "full_name": "Angela Dąbrowska",
                "middle_name": "",
                "family_name": "Dąbrowska",
                "phone_no": "934-25-25-121",
                "phone_no_alternative": "",
                "relationship": SON_DAUGHTER,
                "sex": MALE,
                "birth_date": "1985-08-12",
            },
        ]
        _, self.individuals = create_household_and_individuals(
            household_data=household_data, individuals_data=individuals_data
        )

    def test_generate_report(self):
        # Given
        updater = IndividualXlsxUpdate(self.xlsx_update_file)

        # When
        report = updater.get_matching_report()

        # Then
        self.assertEqual(len(report[IndividualXlsxUpdate.STATUS_UNIQUE]), 2)
        self.assertEqual(len(report[IndividualXlsxUpdate.STATUS_NO_MATCH]), 1)
        self.assertEqual(len(report[IndividualXlsxUpdate.STATUS_MULTIPLE_MATCH]), 1)

    def test_update_individuals(self):
        # Given
        updater = IndividualXlsxUpdate(self.xlsx_update_file)

        # When
        updater.update_individuals()

        # Then
        [individual.refresh_from_db() for individual in self.individuals]

        self.assertEqual(self.individuals[0].family_name, "Dąbrowski")
        self.assertEqual(self.individuals[1].family_name, "Dąbrowska")
        self.assertEqual(self.individuals[2].family_name, "Kowalska")
        self.assertEqual(self.individuals[3].family_name, "Dąbrowska")

    def test_raise_error_when_invalid_columns(self):
        with self.assertRaises(InvalidColumnsError) as context:
            IndividualXlsxUpdate(self.xlsx_update_invalid_file)

        self.assertTrue("Invalid columns" in str(context.exception))
