from datetime import timedelta

from django.utils.timezone import now
import pytest

from extras.test_utils.factories import (
    PaymentFactory,
    PaymentPlanFactory,
    ProgramCycleFactory,
    ProgramFactory,
)
from hope.models import PaymentPlan

pytestmark = pytest.mark.django_db


@pytest.fixture
def program_cycle():
    return ProgramCycleFactory()


def test_can_send_to_vision_returns_true_when_accepted(program_cycle) -> None:
    program = ProgramFactory()
    cycle = program.cycles.first()
    payment_plan = PaymentPlanFactory(
        program_cycle=cycle,
        status=PaymentPlan.Status.ACCEPTED,
    )
    assert payment_plan.can_send_to_vision is True


def test_can_send_to_vision_returns_false_when_not_accepted(program_cycle) -> None:
    program = ProgramFactory()
    cycle = program.cycles.first()
    payment_plan = PaymentPlanFactory(
        program_cycle=cycle,
        status=PaymentPlan.Status.DRAFT,
    )
    assert payment_plan.can_send_to_vision is False


def test_has_payments_reconciliation_overdue_raises_type_error_when_dispersion_start_date_is_none(program_cycle):
    program = ProgramFactory(reconciliation_window_in_days=30)
    cycle = program.cycles.first()
    payment_plan = PaymentPlanFactory(
        program_cycle=cycle,
        status=PaymentPlan.Status.ACCEPTED,
        dispersion_start_date=None,
    )

    with pytest.raises(TypeError):
        _ = payment_plan.has_payments_reconciliation_overdue


def test_has_payments_reconciliation_overdue_returns_false_when_no_reconciliation_window(program_cycle):
    program = ProgramFactory(reconciliation_window_in_days=0)
    cycle = program.cycles.first()
    payment_plan = PaymentPlanFactory(
        program_cycle=cycle,
        status=PaymentPlan.Status.ACCEPTED,
        dispersion_start_date=now().date() - timedelta(days=60),
    )

    assert payment_plan.has_payments_reconciliation_overdue is False


def test_has_payments_reconciliation_overdue_returns_true_when_overdue_and_unreconciled(program_cycle):
    program = ProgramFactory(reconciliation_window_in_days=10)
    cycle = program.cycles.first()
    payment_plan = PaymentPlanFactory(
        program_cycle=cycle,
        status=PaymentPlan.Status.ACCEPTED,
        dispersion_start_date=now().date() - timedelta(days=20),
    )
    PaymentFactory(
        parent=payment_plan,
        delivered_quantity=None,
    )

    assert payment_plan.has_payments_reconciliation_overdue is True
