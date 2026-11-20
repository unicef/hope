from typing import Any

import pytest

from extras.test_utils.factories import PaymentListFactory, PaymentPlanFactory, ProgramCycleFactory
from extras.test_utils.factories.payment import FinancialServiceProviderFactory, FollowUpInstructionFactory
from hope.admin.fsp import FinancialServiceProviderAdminForm
from hope.models import FinancialServiceProvider, PaymentList

pytestmark = pytest.mark.django_db


@pytest.fixture
def fsp_with_payment_lists() -> tuple[FinancialServiceProvider, PaymentList, PaymentList]:
    fsp = FinancialServiceProviderFactory()
    other_fsp = FinancialServiceProviderFactory()
    cycle = ProgramCycleFactory()
    plan = PaymentPlanFactory(cycle=cycle, financial_service_provider=fsp)
    instruction = FollowUpInstructionFactory(program=cycle.program, financial_service_provider=fsp)
    other_plan = PaymentPlanFactory(cycle=cycle, financial_service_provider=other_fsp)

    plan_list = PaymentListFactory(program_cycle=cycle, payment_plan=plan, status=PaymentList.Status.ACCEPTED)
    instruction_list = PaymentListFactory(
        program_cycle=cycle, follow_up_instruction=instruction, status=PaymentList.Status.ACCEPTED
    )
    PaymentListFactory(program_cycle=cycle, payment_plan=plan, status=PaymentList.Status.OPEN)
    PaymentListFactory(program_cycle=cycle, payment_plan=plan, status=PaymentList.Status.FINISHED)
    PaymentListFactory(program_cycle=cycle, payment_plan=other_plan, status=PaymentList.Status.ACCEPTED)
    return fsp, plan_list, instruction_list


def test_locked_payment_lists_for_fsp_uses_both_owners(
    fsp_with_payment_lists: tuple[FinancialServiceProvider, PaymentList, PaymentList],
    django_assert_num_queries: Any,
) -> None:
    fsp, plan_list, instruction_list = fsp_with_payment_lists

    with django_assert_num_queries(1):
        ids = set(FinancialServiceProviderAdminForm.locked_payment_lists_for_fsp(fsp).values_list("pk", flat=True))

    assert ids == {plan_list.pk, instruction_list.pk}
