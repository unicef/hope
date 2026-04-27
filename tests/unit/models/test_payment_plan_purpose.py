from django.core.exceptions import ValidationError
import pytest

from extras.test_utils.factories import (
    PaymentPlanFactory,
    PaymentPlanPurposeFactory,
    ProgramCycleFactory,
    ProgramFactory,
)

pytestmark = pytest.mark.django_db


def test_program_requires_at_least_one_purpose_to_activate():
    program = ProgramFactory(status="DRAFT")
    program.status = "ACTIVE"
    with pytest.raises(ValidationError, match="Program must have at least one Payment Plan Purpose before becoming ACTIVE."):
        program.save()


def test_program_can_have_multiple_purposes():
    program = ProgramFactory(status="DRAFT")
    p1 = PaymentPlanPurposeFactory()
    p2 = PaymentPlanPurposeFactory()
    program.payment_plan_purposes.set([p1, p2])
    program.status = "ACTIVE"
    program.save()
    assert program.payment_plan_purposes.count() == 2


def test_payment_plan_requires_at_least_one_purpose():
    plan = PaymentPlanFactory()

    with pytest.raises(ValidationError, match="PaymentPlan must have at least one Payment Plan Purpose."):
        plan.clean()


def test_payment_plan_purpose_must_be_subset_of_program_purposes():
    purpose_for_program = PaymentPlanPurposeFactory()
    unrelated_purpose = PaymentPlanPurposeFactory()
    program = ProgramFactory(status="ACTIVE")
    program.payment_plan_purposes.add(purpose_for_program)
    cycle = ProgramCycleFactory(program=program)
    plan = PaymentPlanFactory(program_cycle=cycle)
    plan.payment_plan_purposes.add(unrelated_purpose)

    with pytest.raises(ValidationError, match="All PaymentPlan purposes must be a subset of the program's purposes."):
        plan.clean()
