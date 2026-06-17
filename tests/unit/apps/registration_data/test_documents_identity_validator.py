from typing import Any

import pytest
from django.conf import settings

from extras.test_utils.factories.program import ProgramFactory

from hope.apps.registration_data.validators import ImportDataInstanceValidator
from hope.models import Partner, Program


@pytest.fixture(scope="module")
def program(django_db_setup: Any, django_db_blocker: Any) -> Program:
    with django_db_blocker.unblock():
        unicef, _ = Partner.objects.get_or_create(name="UNICEF")
        Partner.objects.get_or_create(name=settings.UNICEF_HQ_PARTNER, parent=unicef)
        return ProgramFactory()


@pytest.fixture
def validator(program: Program) -> ImportDataInstanceValidator:
    return ImportDataInstanceValidator(program)


def test_documents_validator_requires_number_when_issuing_country_present(
    validator: ImportDataInstanceValidator,
) -> None:
    result = validator.documents_validator(
        {"national_id_no_i_c": {"validation_data": [{"row_number": 2}], "numbers": [""], "issuing_countries": ["AF"]}}
    )

    assert result[0]["message"] == "Number for national_id_no_i_c is required, when issuing country is provided"
    assert result[0]["row_number"] == 2


def test_identity_validator_requires_issuing_country_when_number_present(
    validator: ImportDataInstanceValidator,
) -> None:
    result = validator.identity_validator(
        {
            "unhcr_id": {
                "validation_data": [{"row_number": 2}],
                "numbers": ["123"],
                "issuing_countries": [None],
                "partner": "P",
            }
        }
    )

    assert result[0]["message"] == "Issuing country is required: partner: P no: 123"
    assert result[0]["row_number"] == 2


def test_identity_validator_requires_number_when_issuing_country_present(
    validator: ImportDataInstanceValidator,
) -> None:
    result = validator.identity_validator(
        {
            "unhcr_id": {
                "validation_data": [{"row_number": 3}],
                "numbers": [""],
                "issuing_countries": ["AF"],
                "partner": "P",
            }
        }
    )

    assert result[0]["message"] == "Number for unhcr_id is required, when issuing country is provided"
    assert result[0]["row_number"] == 3


def test_identity_validator_non_xlsx_omits_row_number(
    validator: ImportDataInstanceValidator,
) -> None:
    result = validator.identity_validator(
        {
            "unhcr_id": {
                "validation_data": [{"row_number": 4}],
                "numbers": ["123"],
                "issuing_countries": [None],
                "partner": "P",
            }
        },
        is_xlsx=False,
    )

    assert "row_number" not in result[0]
