import datetime
from io import BytesIO
from pathlib import Path

from django.conf import settings
from django.core.files import File

from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.household.fixtures import create_household_and_individuals
from hct_mis_api.apps.household.models import (
    FEMALE,
    HEAD,
    MALE,
    SON_DAUGHTER,
    WIFE_HUSBAND,
    XlsxUpdateFile,
)
from hct_mis_api.apps.household.services.individual_xlsx_update import (
    IndividualXlsxUpdate,
    InvalidColumnsError,
)
from hct_mis_api.apps.registration_data.fixtures import RegistrationDataImportFactory


def valid_file():
    content = Path(f"{settings.PROJECT_ROOT}/apps/household/tests/test_file/valid_updated_test_file.xlsx").read_bytes()
    return File(BytesIO(content), name="valid_updated_test_file.xlsx")


def valid_file_complex():
    content = Path(
        f"{settings.PROJECT_ROOT}/apps/household/tests/test_file/valid_updated_test_file_complex.xlsx"
    ).read_bytes()
    return File(BytesIO(content), name="valid_updated_test_file_complex.xlsx")


def invalid_file():
    content = Path(
        f"{settings.PROJECT_ROOT}/apps/household/tests/test_file/invalid_updated_test_file.xlsx"
    ).read_bytes()
    return File(BytesIO(content), name="invalid_updated_test_file.xlsx")


class TestIndividualXlsxUpdate(APITestCase):
    databases = "__all__"

    @classmethod
    def setUpTestData(cls):
        create_afghanistan()
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")

        registration_data_import = RegistrationDataImportFactory(business_area=cls.business_area)
        cls.xlsx_update_file = XlsxUpdateFile.objects.create(
            file=valid_file(),
            business_area=cls.business_area,
            xlsx_match_columns=["individual__given_name"],
        )

        cls.xlsx_update_invalid_file = XlsxUpdateFile.objects.create(
            file=invalid_file(),
            business_area=cls.business_area,
            xlsx_match_columns=["individual__given_name"],
        )

        cls.xlsx_update_valid_file_complex = XlsxUpdateFile.objects.create(
            file=valid_file_complex(),
            business_area=cls.business_area,
            xlsx_match_columns=["individual__full_name"],
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
        _, cls.individuals = create_household_and_individuals(
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

    def test_complex_update_individual(self):
        # Given
        updater = IndividualXlsxUpdate(self.xlsx_update_valid_file_complex)

        # When
        updater.update_individuals()

        # Then
        [individual.refresh_from_db() for individual in self.individuals]

        self.assertEqual(self.individuals[0].family_name, "Kowalski")
        self.assertEqual(self.individuals[1].family_name, "Kowalska")
        self.assertEqual(self.individuals[2].family_name, "Kowalska")
        self.assertEqual(self.individuals[3].family_name, "Dąbrowska")

        self.assertEqual(self.individuals[0].given_name, "Patryk")
        self.assertEqual(self.individuals[1].given_name, "Karolina")
        self.assertEqual(self.individuals[2].given_name, "Angela")
        self.assertEqual(self.individuals[3].given_name, "Angela")

        self.assertEqual(self.individuals[0].full_name, "Patryk Kowalski")
        self.assertEqual(self.individuals[1].full_name, "Karolina Kowalska")
        self.assertEqual(self.individuals[2].full_name, "Angela Kowalska")
        self.assertEqual(self.individuals[3].full_name, "Angela Dąbrowska")

        self.assertEqual(self.individuals[0].phone_no, "934-25-25-197")
        self.assertEqual(self.individuals[1].phone_no, "934-25-25-198")
        self.assertEqual(self.individuals[2].phone_no, "934-25-25-199")
        self.assertEqual(self.individuals[3].phone_no, "934-25-25-121")

        self.assertEqual(self.individuals[0].birth_date, datetime.date(1965, 8, 5))
        self.assertEqual(self.individuals[1].birth_date, datetime.date(1965, 8, 6))
        self.assertEqual(self.individuals[2].birth_date, datetime.date(1965, 8, 7))
        self.assertEqual(self.individuals[3].birth_date, datetime.date(1985, 8, 12))
