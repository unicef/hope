import pytest

from extras.test_utils.factories import (
    DeliveryMechanismFactory,
    FinancialServiceProviderFactory,
    PaymentListFactory,
    PaymentVerificationPlanFactory,
)
from extras.test_utils.factories.program import ProgramFactory
from hope.models import BusinessArea, PaymentList, PaymentVerificationPlan, Program


@pytest.fixture
def pending_verification_payment_list(business_area: BusinessArea) -> PaymentList:
    """FINISHED payment plan in an ACTIVE program with a single PENDING verification plan.

    The MANUAL verification channel is used on purpose: it keeps activation deterministic
    by skipping the RapidPro path entirely (no external service to mock). The program must
    be ACTIVE so the frontend Activate button is enabled (it is disabled otherwise).
    """
    program = ProgramFactory(business_area=business_area, status=Program.ACTIVE)
    payment_list = PaymentListFactory(
        business_area=business_area,
        program_cycle=program.cycles.first(),
        status=PaymentList.Status.FINISHED,
        financial_service_provider=FinancialServiceProviderFactory(),
        delivery_mechanism=DeliveryMechanismFactory(),
    )
    PaymentVerificationPlanFactory(
        payment_list=payment_list,
        verification_channel=PaymentVerificationPlan.VERIFICATION_CHANNEL_MANUAL,
        sampling="FULL_LIST",
    )
    return payment_list
