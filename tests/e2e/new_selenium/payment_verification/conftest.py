import pytest

from extras.test_utils.factories import (
    DeliveryMechanismFactory,
    FinancialServiceProviderFactory,
    PaymentPlanFactory,
    PaymentVerificationPlanFactory,
)
from extras.test_utils.factories.program import ProgramFactory
from hope.models import BusinessArea, PaymentPlan, PaymentVerificationPlan, Program


@pytest.fixture
def pending_verification_payment_plan(business_area: BusinessArea) -> PaymentPlan:
    """FINISHED payment plan in an ACTIVE program with a single PENDING verification plan.

    The MANUAL verification channel is used on purpose: it keeps activation deterministic
    by skipping the RapidPro path entirely (no external service to mock). The program must
    be ACTIVE so the frontend Activate button is enabled (it is disabled otherwise).
    """
    program = ProgramFactory(business_area=business_area, status=Program.ACTIVE)
    payment_plan = PaymentPlanFactory(
        business_area=business_area,
        program_cycle=program.cycles.first(),
        status=PaymentPlan.Status.FINISHED,
        financial_service_provider=FinancialServiceProviderFactory(),
        delivery_mechanism=DeliveryMechanismFactory(),
    )
    PaymentVerificationPlanFactory(
        payment_plan=payment_plan,
        verification_channel=PaymentVerificationPlan.VERIFICATION_CHANNEL_MANUAL,
        sampling="FULL_LIST",
    )
    return payment_plan
