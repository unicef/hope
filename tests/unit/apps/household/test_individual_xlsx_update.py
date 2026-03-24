import datetime
from io import BytesIO
from pathlib import Path

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files import File
import pytest

from extras.test_utils.factories import (
    BusinessAreaFactory,
    HouseholdFactory,
    IndividualFactory,
    ProgramFactory,
    RegistrationDataImportFactory,
    XlsxUpdateFileFactory,
)
from hope.apps.household.const import FEMALE, HEAD, MALE, OTHER, SON_DAUGHTER, WIFE_HUSBAND
from hope.apps.household.services.individual_xlsx_update import IndividualXlsxUpdate, InvalidColumnsError

pytestmark = pytest.mark.django_db


@pytest.fixture
def business_area():
    return BusinessAreaFactory(slug="afghanistan", name="Afghanistan")


@pytest.fixture
def program(business_area):
    return ProgramFactory(business_area=business_area)


@pytest.fixture
def registration_data_import(business_area, program):
    return RegistrationDataImportFactory(business_area=business_area, program=program)


@pytest.fixture
def household(business_area, program, registration_data_import):
    return HouseholdFactory(
        business_area=business_area,
        program=program,
        registration_data_import=registration_data_import,
        create_role=False,
        size=4,
    )


@pytest.fixture
def individuals(household, business_area, program, registration_data_import):
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
    individuals = [
        IndividualFactory(
            household=household,
            business_area=business_area,
            program=program,
            **individual_data,
        )
        for individual_data in individuals_data
    ]
    household.head_of_household = individuals[0]
    household.save(update_fields=["head_of_household"])
    return individuals


@pytest.fixture
def valid_file():
    content = Path(f"{settings.TESTS_ROOT}/apps/household/test_file/valid_updated_test_file.xlsx").read_bytes()
    return File(BytesIO(content), name="valid_updated_test_file.xlsx")


@pytest.fixture
def valid_file_complex():
    content = Path(f"{settings.TESTS_ROOT}/apps/household//test_file/valid_updated_test_file_complex.xlsx").read_bytes()
    return File(BytesIO(content), name="valid_updated_test_file_complex.xlsx")


@pytest.fixture
def invalid_file():
    content = Path(f"{settings.TESTS_ROOT}/apps/household/test_file/invalid_updated_test_file.xlsx").read_bytes()
    return File(BytesIO(content), name="invalid_updated_test_file.xlsx")


@pytest.fixture
def invalid_phone_no_file():
    content = Path(
        f"{settings.TESTS_ROOT}/apps/household/test_file/invalid_updated_test_file_wrong_phone_no.xlsx"
    ).read_bytes()
    return File(BytesIO(content), name="invalid_updated_phone_no_test_file.xlsx")


@pytest.fixture
def xlsx_update_file(business_area, valid_file):
    return XlsxUpdateFileFactory(
        file=valid_file,
        business_area=business_area,
        xlsx_match_columns=["individual__given_name"],
    )


@pytest.fixture
def xlsx_update_invalid_file(business_area, invalid_file):
    return XlsxUpdateFileFactory(
        file=invalid_file,
        business_area=business_area,
        xlsx_match_columns=["individual__given_name"],
    )


@pytest.fixture
def xlsx_update_valid_file_complex(business_area, valid_file_complex):
    return XlsxUpdateFileFactory(
        file=valid_file_complex,
        business_area=business_area,
        xlsx_match_columns=["individual__full_name"],
    )


@pytest.fixture
def xlsx_update_invalid_phone_no_file(business_area, invalid_phone_no_file):
    return XlsxUpdateFileFactory(
        file=invalid_phone_no_file,
        business_area=business_area,
        xlsx_match_columns=["individual__given_name"],
    )


def test_generate_report(xlsx_update_file, individuals) -> None:
    updater = IndividualXlsxUpdate(xlsx_update_file)

    report = updater.get_matching_report()

    assert len(report[IndividualXlsxUpdate.STATUS_UNIQUE]) == 2
    assert len(report[IndividualXlsxUpdate.STATUS_NO_MATCH]) == 1
    assert len(report[IndividualXlsxUpdate.STATUS_MULTIPLE_MATCH]) == 1


def test_update_individuals(xlsx_update_file, individuals) -> None:
    updater = IndividualXlsxUpdate(xlsx_update_file)

    updater.update_individuals()

    [individual.refresh_from_db() for individual in individuals]

    assert individuals[0].family_name == "Dąbrowski"
    assert individuals[1].family_name == "Dąbrowska"
    assert individuals[2].family_name == "Kowalska"
    assert individuals[3].family_name == "Dąbrowska"


def test_raise_error_when_invalid_columns(xlsx_update_invalid_file) -> None:
    with pytest.raises(InvalidColumnsError) as context:
        IndividualXlsxUpdate(xlsx_update_invalid_file)

    assert "Invalid columns" in str(context.value)


def test_complex_update_individual(xlsx_update_valid_file_complex, individuals) -> None:
    updater = IndividualXlsxUpdate(xlsx_update_valid_file_complex)

    updater.update_individuals()

    [individual.refresh_from_db() for individual in individuals]

    assert individuals[0].family_name == "Kowalski"
    assert individuals[1].family_name == "Kowalska"
    assert individuals[2].family_name == "Kowalska"
    assert individuals[3].family_name == "Dąbrowska"

    assert individuals[0].given_name == "Patryk"
    assert individuals[1].given_name == "Karolina"
    assert individuals[2].given_name == "Angela"
    assert individuals[3].given_name == "Angela"

    assert individuals[0].full_name == "Patryk Kowalski"
    assert individuals[1].full_name == "Karolina Kowalska"
    assert individuals[2].full_name == "Angela Kowalska"
    assert individuals[3].full_name == "Angela Dąbrowska"

    assert individuals[0].phone_no == "934-25-25-197"
    assert individuals[1].phone_no == "934-25-25-198"
    assert individuals[2].phone_no == "934-25-25-199"
    assert individuals[3].phone_no == "934-25-25-121"

    assert individuals[0].birth_date == datetime.date(1965, 8, 5)
    assert individuals[1].birth_date == datetime.date(1965, 8, 6)
    assert individuals[2].birth_date == datetime.date(1965, 8, 7)
    assert individuals[3].birth_date == datetime.date(1985, 8, 12)


def test_raise_error_when_invalid_phone_number(xlsx_update_invalid_phone_no_file, individuals) -> None:
    with pytest.raises(ValidationError) as context:
        IndividualXlsxUpdate(xlsx_update_invalid_phone_no_file).update_individuals()

    assert str({"phone_no": [f"Invalid phone number for individual {individuals[0]}."]}) == str(context.value)
