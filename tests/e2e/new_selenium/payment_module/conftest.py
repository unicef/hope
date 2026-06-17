import pytest

from extras.test_utils.factories import (
    DeliveryMechanismFactory,
    FinancialServiceProviderFactory,
    PaymentPlanFactory,
    ProgramFactory,
)
from hope.models import BusinessArea, PaymentPlan, Program, User


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


@pytest.fixture
def ready_for_closure_payment_plan(business_area: BusinessArea) -> PaymentPlan:
    program = ProgramFactory(business_area=business_area, status=Program.ACTIVE)
    return PaymentPlanFactory(
        business_area=business_area,
        program_cycle=program.cycles.first(),
        status=PaymentPlan.Status.READY_FOR_CLOSURE,
        financial_service_provider=FinancialServiceProviderFactory(),
        delivery_mechanism=DeliveryMechanismFactory(),
    )


@pytest.fixture
def closed_payment_plan(business_area: BusinessArea) -> PaymentPlan:
    user = User.objects.filter(username="superuser").first()
    program = ProgramFactory(business_area=business_area, status=Program.ACTIVE)
    pp = PaymentPlanFactory(
        business_area=business_area,
        program_cycle=program.cycles.first(),
        status=PaymentPlan.Status.CLOSED,
        financial_service_provider=FinancialServiceProviderFactory(),
        delivery_mechanism=DeliveryMechanismFactory(),
    )
    pp.closed_by = user
    pp.save(update_fields=["closed_by"])
    return pp
