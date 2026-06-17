from typing import Any

import pytest

from extras.test_utils.factories import (
    ApprovalProcessFactory,
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
def closed_payment_plan(business_area: BusinessArea, create_super_user: Any) -> PaymentPlan:
    program = ProgramFactory(business_area=business_area, status=Program.ACTIVE)
    pp = PaymentPlanFactory(
        business_area=business_area,
        program_cycle=program.cycles.first(),
        status=PaymentPlan.Status.CLOSED,
        financial_service_provider=FinancialServiceProviderFactory(),
        delivery_mechanism=DeliveryMechanismFactory(),
    )
    pp.closed_by = create_super_user
    pp.save(update_fields=["closed_by"])
    ApprovalProcessFactory(payment_plan=pp)
    return pp
