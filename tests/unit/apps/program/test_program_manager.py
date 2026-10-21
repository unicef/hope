"""Tests for program manager functionality."""

from typing import Any
from unittest.mock import patch

from django.core.exceptions import ValidationError
import pytest

from extras.test_utils.factories import (
    BeneficiaryGroupFactory,
    BusinessAreaFactory,
    DataCollectingTypeFactory,
    PayeeTypeFactory,
    ProgramFactory,
)
from hope.models import BeneficiaryGroup, BusinessArea, DataCollectingType, PayeeType, Program

pytestmark = pytest.mark.django_db


@pytest.fixture
def afghanistan(db: Any) -> BusinessArea:
    return BusinessAreaFactory(name="Afghanistan", slug="afghanistan")


@pytest.fixture
def household_payee_type(db: Any) -> PayeeType:
    return PayeeTypeFactory(name="Household", gl_code="7700410")


@pytest.fixture
def incentive_payee_type(db: Any) -> PayeeType:
    return PayeeTypeFactory(name="Incentive Payee", gl_code="7700430")


@pytest.fixture
def household_dct(household_payee_type: PayeeType) -> DataCollectingType:
    return DataCollectingTypeFactory(code="full_collection", payee_type=household_payee_type)


@pytest.fixture
def frontline_dct(incentive_payee_type: PayeeType) -> DataCollectingType:
    return DataCollectingTypeFactory(
        code="frontline_worker_wash", type=DataCollectingType.Type.SOCIAL, payee_type=incentive_payee_type
    )


@pytest.fixture
def household_label(household_payee_type: PayeeType) -> BeneficiaryGroup:
    return BeneficiaryGroupFactory(name="Households", payee_type=household_payee_type)


@pytest.fixture
def wash_workers_label(incentive_payee_type: PayeeType) -> BeneficiaryGroup:
    return BeneficiaryGroupFactory(name="WASH workers", payee_type=incentive_payee_type)


@pytest.fixture
def household_program(
    afghanistan: BusinessArea, household_dct: DataCollectingType, household_label: BeneficiaryGroup
) -> Program:
    return ProgramFactory(
        business_area=afghanistan, data_collecting_type=household_dct, beneficiary_group=household_label
    )


@pytest.fixture
def program_with_inactive_household_label(household_program: Program, household_label: BeneficiaryGroup) -> Program:
    household_label.active = False
    household_label.save()
    return household_program


def test_get_by_unicef_id_returns_program(afghanistan: BusinessArea) -> None:
    program = ProgramFactory(business_area=afghanistan, code="ab12")

    result = Program.objects.get_by_unicef_id(f"{afghanistan.slug}-{program.code}")

    assert result == program


def test_get_by_unicef_id_not_found(afghanistan: BusinessArea) -> None:
    with pytest.raises(Program.DoesNotExist) as exc_info:
        Program.objects.get_by_unicef_id("missing-id")

    assert str(exc_info.value) == "Program matching unicef_id 'missing-id' does not exist."


def test_generate_code_retries_on_collision(afghanistan: BusinessArea) -> None:
    existing = ProgramFactory(business_area=afghanistan, code="ab12")
    new_program = ProgramFactory.build(business_area=afghanistan, code="")

    with patch("hope.models.program.secrets.choice", side_effect=list("ab12") + list("zz99")):
        code = new_program.generate_code()

    assert code == "zz99"
    assert code != existing.code


def test_program_save_rejects_payee_label_of_other_payee_type(
    afghanistan: BusinessArea, household_dct: DataCollectingType, wash_workers_label: BeneficiaryGroup
) -> None:
    with pytest.raises(ValidationError) as error:
        ProgramFactory(
            business_area=afghanistan, data_collecting_type=household_dct, beneficiary_group=wash_workers_label
        )

    assert error.value.message_dict == {
        "beneficiary_group": ["Payee Label does not belong to the selected Payee Type."]
    }


def test_program_save_rejects_changing_dct_to_other_payee_type(
    household_program: Program, frontline_dct: DataCollectingType
) -> None:
    household_program.data_collecting_type = frontline_dct

    with pytest.raises(ValidationError) as error:
        household_program.save()

    assert error.value.message_dict == {
        "beneficiary_group": ["Payee Label does not belong to the selected Payee Type."]
    }


def test_program_save_with_unchanged_inactive_payee_label_succeeds(
    program_with_inactive_household_label: Program,
) -> None:
    program_with_inactive_household_label.household_count = 5

    program_with_inactive_household_label.save()

    program_with_inactive_household_label.refresh_from_db()
    assert program_with_inactive_household_label.household_count == 5
