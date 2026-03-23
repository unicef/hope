from datetime import timedelta
from unittest.mock import patch

from django.utils.timezone import now
import pytest

from extras.test_utils.factories import (
    ApprovalProcessFactory,
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


@pytest.fixture
def payment_plan(program_cycle):
    return PaymentPlanFactory(program_cycle=program_cycle)


def test_get_last_approval_process_data_raises_value_error_when_sent_for_approval_date_is_none(program_cycle):
    payment_plan = PaymentPlanFactory(
        program_cycle=program_cycle,
        status=PaymentPlan.Status.IN_APPROVAL,
    )
    ApprovalProcessFactory(
        payment_plan=payment_plan,
        sent_for_approval_date=None,
    )
    payment_plan.refresh_from_db()

    with pytest.raises(ValueError, match="sent_for_approval_date must not be None"):
        payment_plan._get_last_approval_process_data()


def test_get_unore_exchange_rate_raises_value_error_when_currency_is_none(payment_plan):
    payment_plan.currency = None

    with pytest.raises(ValueError, match="currency must not be None"):
        payment_plan.get_unore_exchange_rate()


def test_has_payments_reconciliation_overdue_returns_false_when_dispersion_start_date_is_none(program_cycle):
    program = ProgramFactory(reconciliation_window_in_days=30)
    cycle = ProgramCycleFactory(program=program)
    payment_plan = PaymentPlanFactory(
        program_cycle=cycle,
        status=PaymentPlan.Status.ACCEPTED,
        dispersion_start_date=None,
    )

    assert payment_plan.has_payments_reconciliation_overdue is False


def test_has_payments_reconciliation_overdue_returns_false_when_no_reconciliation_window(program_cycle):
    program = ProgramFactory(reconciliation_window_in_days=0)
    cycle = ProgramCycleFactory(program=program)
    payment_plan = PaymentPlanFactory(
        program_cycle=cycle,
        status=PaymentPlan.Status.ACCEPTED,
        dispersion_start_date=now().date() - timedelta(days=60),
    )

    assert payment_plan.has_payments_reconciliation_overdue is False


def test_has_payments_reconciliation_overdue_returns_true_when_overdue_and_unreconciled(program_cycle):
    program = ProgramFactory(reconciliation_window_in_days=10)
    cycle = ProgramCycleFactory(program=program)
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
