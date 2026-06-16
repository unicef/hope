import pytest

from extras.test_utils.factories import (
    DeliveryMechanismFactory,
    FinancialServiceProviderFactory,
    PaymentPlanFactory,
    ProgramFactory,
)
from hope.models import BusinessArea, PaymentPlan, Program


@pytest.fixture
def finished_payment_plan(business_area: BusinessArea) -> PaymentPlan:
    program = ProgramFactory(business_area=business_area, status=Program.ACTIVE)
    return PaymentPlanFactory(
        business_area=business_area,
        program_cycle=program.cycles.first(),
        status=PaymentPlan.Status.FINISHED,
        financial_service_provider=FinancialServiceProviderFactory(),
        delivery_mechanism=DeliveryMechanismFactory(),
    )
