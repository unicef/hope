from django.core.exceptions import ValidationError
import pytest

from extras.test_utils.factories import PaymentPlanFactory, PaymentPlanGroupFactory, ProgramCycleFactory
from hope.models import PaymentPlanGroup

pytestmark = pytest.mark.django_db


@pytest.fixture
def cycle():
    return ProgramCycleFactory()


@pytest.fixture
def payment_plan_group(cycle):
    return PaymentPlanGroupFactory(cycle=cycle)


def test_default_group_created_on_cycle_creation(cycle):
    assert PaymentPlanGroup.objects.filter(cycle=cycle, name="Default Group").exists()


def test_payment_plan_with_matching_group_saves_without_error(cycle, payment_plan_group):
    PaymentPlanFactory(program_cycle=cycle, payment_plan_group=payment_plan_group)


def test_payment_plan_group_cycle_must_match_plan_cycle(cycle, payment_plan_group):
    other_cycle = ProgramCycleFactory(program=cycle.program)
    plan = PaymentPlanFactory(program_cycle=cycle, payment_plan_group=payment_plan_group)

    plan.program_cycle = other_cycle

    with pytest.raises(ValidationError, match="aymentPlan's program_cycle must match its PaymentPlanGroup's cycle."):
        plan.save()


def test_default_group_not_created_again_on_cycle_update(cycle):
    group_count_before = PaymentPlanGroup.objects.filter(cycle=cycle).count()

    cycle.title = "Updated Title"
    cycle.save()

    assert PaymentPlanGroup.objects.filter(cycle=cycle).count() == group_count_before
