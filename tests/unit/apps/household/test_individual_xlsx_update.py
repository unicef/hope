import datetime
from io import BytesIO
from pathlib import Path

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files import File
from extras.test_utils.factories.core import create_afghanistan
from extras.test_utils.factories.household import create_household_and_individuals
from extras.test_utils.factories.registration_data import RegistrationDataImportFactory

from hope.apps.core.base_test_case import BaseTestCase
from hope.models.business_area import BusinessArea
from hope.models.household import (
    FEMALE,
    HEAD,
    MALE,
    OTHER,
    SON_DAUGHTER,
    WIFE_HUSBAND,
)
from hope.models.xlsx_update_file import XlsxUpdateFile
from hope.apps.household.services.individual_xlsx_update import (
    IndividualXlsxUpdate,
    InvalidColumnsError,
)


def valid_file() -> File:
    content = Path(f"{settings.TESTS_ROOT}/apps/household/test_file/valid_updated_test_file.xlsx").read_bytes()
    return File(BytesIO(content), name="valid_updated_test_file.xlsx")


def valid_file_complex() -> File:
    content = Path(f"{settings.TESTS_ROOT}/apps/household//test_file/valid_updated_test_file_complex.xlsx").read_bytes()
    return File(BytesIO(content), name="valid_updated_test_file_complex.xlsx")


def invalid_file() -> File:
    content = Path(f"{settings.TESTS_ROOT}/apps/household/test_file/invalid_updated_test_file.xlsx").read_bytes()
    return File(BytesIO(content), name="invalid_updated_test_file.xlsx")


def invalid_phone_no_file() -> File:
    content = Path(
        f"{settings.TESTS_ROOT}/apps/household/test_file/invalid_updated_test_file_wrong_phone_no.xlsx"
    ).read_bytes()
    return File(BytesIO(content), name="invalid_updated_phone_no_test_file.xlsx")


class TestIndividualXlsxUpdate(BaseTestCase):
    databases = "__all__"

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
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

        cls.xlsx_update_invalid_phone_no_file = XlsxUpdateFile.objects.create(
            file=invalid_phone_no_file(),
            business_area=cls.business_area,
            xlsx_match_columns=["individual__given_name"],
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
                "sex": OTHER,
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

    def test_generate_report(self) -> None:
        # Given
        updater = IndividualXlsxUpdate(self.xlsx_update_file)

        # When
        report = updater.get_matching_report()

        # Then
        assert len(report[IndividualXlsxUpdate.STATUS_UNIQUE]) == 2
        assert len(report[IndividualXlsxUpdate.STATUS_NO_MATCH]) == 1
        assert len(report[IndividualXlsxUpdate.STATUS_MULTIPLE_MATCH]) == 1

    def test_update_individuals(self) -> None:
        # Given
        updater = IndividualXlsxUpdate(self.xlsx_update_file)

        # When
        updater.update_individuals()

        # Then
        [individual.refresh_from_db() for individual in self.individuals]

        assert self.individuals[0].family_name == "Dąbrowski"
        assert self.individuals[1].family_name == "Dąbrowska"
        assert self.individuals[2].family_name == "Kowalska"
        assert self.individuals[3].family_name == "Dąbrowska"

    def test_raise_error_when_invalid_columns(self) -> None:
        with self.assertRaises(InvalidColumnsError) as context:
            IndividualXlsxUpdate(self.xlsx_update_invalid_file)

        assert "Invalid columns" in str(context.exception)

    def test_complex_update_individual(self) -> None:
        # Given
        updater = IndividualXlsxUpdate(self.xlsx_update_valid_file_complex)

        # When
        updater.update_individuals()

        # Then
        [individual.refresh_from_db() for individual in self.individuals]

        assert self.individuals[0].family_name == "Kowalski"
        assert self.individuals[1].family_name == "Kowalska"
        assert self.individuals[2].family_name == "Kowalska"
        assert self.individuals[3].family_name == "Dąbrowska"

        assert self.individuals[0].given_name == "Patryk"
        assert self.individuals[1].given_name == "Karolina"
        assert self.individuals[2].given_name == "Angela"
        assert self.individuals[3].given_name == "Angela"

        assert self.individuals[0].full_name == "Patryk Kowalski"
        assert self.individuals[1].full_name == "Karolina Kowalska"
        assert self.individuals[2].full_name == "Angela Kowalska"
        assert self.individuals[3].full_name == "Angela Dąbrowska"

        assert self.individuals[0].phone_no == "934-25-25-197"
        assert self.individuals[1].phone_no == "934-25-25-198"
        assert self.individuals[2].phone_no == "934-25-25-199"
        assert self.individuals[3].phone_no == "934-25-25-121"

        assert self.individuals[0].birth_date == datetime.date(1965, 8, 5)
        assert self.individuals[1].birth_date == datetime.date(1965, 8, 6)
        assert self.individuals[2].birth_date == datetime.date(1965, 8, 7)
        assert self.individuals[3].birth_date == datetime.date(1985, 8, 12)

    def test_raise_error_when_invalid_phone_number(self) -> None:
        with self.assertRaises(ValidationError) as context:
            IndividualXlsxUpdate(self.xlsx_update_invalid_phone_no_file).update_individuals()

        assert str({"phone_no": [f"Invalid phone number for individual {self.individuals[0]}."]}) == str(
            context.exception
        )
