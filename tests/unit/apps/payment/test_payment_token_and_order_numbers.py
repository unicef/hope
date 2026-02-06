from typing import Any

from django.core.exceptions import ValidationError
from django.db import IntegrityError
import pytest

from extras.test_utils.factories import (
    BusinessAreaFactory,
    CountryFactory,
    HouseholdFactory,
    PaymentFactory,
    PaymentPlanFactory,
    ProgramCycleFactory,
    ProgramFactory,
)
from hope.apps.payment.validators import payment_token_and_order_number_validator
from hope.apps.payment.xlsx.xlsx_payment_plan_export_per_fsp_service import XlsxPaymentPlanExportPerFspService
from hope.models import Payment, PaymentPlan

pytestmark = pytest.mark.django_db


@pytest.fixture
def business_area() -> Any:
    return BusinessAreaFactory(slug="afghanistan")


@pytest.fixture
def country_origin() -> Any:
    return CountryFactory(
        name="Ukraine",
        short_name="Ukraine",
        iso_code2="UA",
        iso_code3="UKR",
        iso_num="0804",
    )


@pytest.fixture
def program(business_area: Any) -> Any:
    return ProgramFactory(business_area=business_area)


@pytest.fixture
def program_cycle(program: Any) -> Any:
    return ProgramCycleFactory(program=program, title="Cycle Token")


@pytest.fixture
def payment_plan(business_area: Any, program_cycle: Any) -> PaymentPlan:
    return PaymentPlanFactory(
        program_cycle=program_cycle,
        status=PaymentPlan.Status.ACCEPTED,
        business_area=business_area,
    )


@pytest.fixture
def households(program: Any, business_area: Any, country_origin: Any) -> list[Any]:
    return [
        HouseholdFactory(
            size=1,
            address="Lorem Ipsum 1",
            country_origin=country_origin,
            program=program,
            business_area=business_area,
        ),
        HouseholdFactory(
            size=2,
            address="Lorem Ipsum 2",
            country_origin=country_origin,
            program=program,
            business_area=business_area,
        ),
    ]


@pytest.fixture
def payments(payment_plan: PaymentPlan, program: Any, households: list[Any]) -> list[Any]:
    return [
        PaymentFactory(
            parent=payment_plan,
            household=household,
            program=program,
            currency="PLN",
        )
        for household in households
    ]


def test_generate_token_and_order_numbers_for_payments(
    payment_plan: PaymentPlan, program: Any, payments: list[Payment]
) -> None:
    service = XlsxPaymentPlanExportPerFspService(payment_plan, None)
    service.generate_token_and_order_numbers(payment_plan.eligible_payments.all(), program)
    payment = payment_plan.eligible_payments.first()
    assert len(str(payment.order_number)) == 9
    assert len(str(payment.token_number)) == 7


def test_validation_token_must_not_has_the_same_digit_more_than_three_times() -> None:
    with pytest.raises(ValidationError):
        payment_token_and_order_number_validator(1111111)


def test_validation_save_payment_with_exists_token_or_order_number(payments: list[Payment]) -> None:
    payment_1 = payments[0]
    payment_2 = payments[1]

    token_number = 1112223
    order_number = 111222333

    payment_1.token_number = token_number
    payment_1.order_number = order_number
    payment_1.save()

    payment_2.token_number = token_number
    payment_2.order_number = order_number
    with pytest.raises(IntegrityError):
        payment_2.save(update_fields=["order_number", "token_number"])
