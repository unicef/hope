from datetime import date
from typing import Any

import pytest

from extras.test_utils.factories import (
    BusinessAreaFactory,
    HouseholdFactory,
    PaymentFactory,
    PaymentPlanFactory,
    ProgramCycleFactory,
    ProgramFactory,
    UserFactory,
)
from hope.apps.payment.services.payment_plan_services import PaymentPlanService
from hope.models import Payment

pytestmark = pytest.mark.django_db


@pytest.fixture
def payment_plan_context() -> dict[str, Any]:
    business_area = BusinessAreaFactory()
    user = UserFactory()
    program = ProgramFactory(business_area=business_area)
    cycle = ProgramCycleFactory(program=program)
    payment_plan = PaymentPlanFactory(
        dispersion_start_date=date(2020, 8, 10),
        dispersion_end_date=date(2020, 12, 10),
        created_by=user,
        business_area=business_area,
        program_cycle=cycle,
    )

    households = [
        HouseholdFactory(business_area=business_area, program=program),
        HouseholdFactory(business_area=business_area, program=program),
        HouseholdFactory(business_area=business_area, program=program),
    ]
    payment_ids = [
        "RCPT-0060-23-0.000.001",
        "RCPT-0060-23-0.000.002",
        "RCPT-0060-23-0.000.003",
    ]
    for household, unicef_id in zip(households, payment_ids, strict=True):
        PaymentFactory(
            parent=payment_plan,
            unicef_id=unicef_id,
            household=household,
            head_of_household=household.head_of_household,
            collector=household.head_of_household,
            entitlement_quantity=212,
            delivered_quantity=150,
            currency="PLN",
        )

    return {
        "payment_plan": payment_plan,
    }


def test_number_of_queries(payment_plan_context: dict[str, Any], django_assert_num_queries: Any) -> None:
    Payment.objects.all().update(signature_hash="")
    assert Payment.objects.filter(signature_hash="").count() == 3
    assert Payment.objects.exclude(signature_hash="").count() == 0
    with django_assert_num_queries(5):
        PaymentPlanService(payment_plan_context["payment_plan"]).recalculate_signatures_in_batch(2)
    assert Payment.objects.filter(signature_hash="").count() == 0
    assert Payment.objects.exclude(signature_hash="").count() == 3
