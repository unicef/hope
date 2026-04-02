from unittest.mock import MagicMock, patch

import pytest

from extras.test_utils.factories import (
    PaymentFactory,
    PaymentPlanFactory,
    ProgramCycleFactory,
)
from hope.apps.payment.services.payment_plan_services import PaymentPlanService
from hope.models import PaymentPlan, PaymentPlanSplit

pytestmark = pytest.mark.django_db


@pytest.fixture
def program_cycle():
    return ProgramCycleFactory()


@pytest.fixture
def payment_plan(program_cycle):
    return PaymentPlanFactory(
        program_cycle=program_cycle,
        status=PaymentPlan.Status.LOCKED,
    )


@pytest.fixture
def payment_plan_with_payments(payment_plan):
    for _ in range(PaymentPlanSplit.MIN_NO_OF_PAYMENTS_IN_CHUNK + 1):
        PaymentFactory(parent=payment_plan)
    return payment_plan


@patch("hope.apps.payment.services.payment_plan_services.config")
def test_validate_acceptance_raises_type_error_when_required_number_is_none(mock_config, payment_plan):
    mock_config.PM_ACCEPTANCE_PROCESS_USER_HAVE_MULTIPLE_APPROVALS = True
    service = PaymentPlanService(payment_plan=payment_plan)
    service.action = PaymentPlan.Action.APPROVE.value
    approval_process = MagicMock()

    with patch.object(service, "get_required_number_by_approval_type", return_value=None):
        with pytest.raises(TypeError):
            service.validate_acceptance_process_approval_count(approval_process)


def test_check_payment_plan_and_update_status_raises_type_error_when_required_number_is_none(payment_plan):
    service = PaymentPlanService(payment_plan=payment_plan)
    service.action = PaymentPlan.Action.APPROVE.value
    approval_process = MagicMock()

    with patch.object(service, "get_required_number_by_approval_type", return_value=None):
        with pytest.raises(TypeError):
            service.check_payment_plan_and_update_status(approval_process)


@patch("hope.apps.payment.services.payment_plan_services.config")
def test_validate_acceptance_does_not_raise_when_count_below_required(mock_config, payment_plan):
    mock_config.PM_ACCEPTANCE_PROCESS_USER_HAVE_MULTIPLE_APPROVALS = True
    service = PaymentPlanService(payment_plan=payment_plan)
    service.action = PaymentPlan.Action.APPROVE.value
    approval_process = MagicMock()
    approval_process.approvals.filter.return_value.count.return_value = 0

    with patch.object(service, "get_required_number_by_approval_type", return_value=5):
        service.validate_acceptance_process_approval_count(approval_process)


def test_check_payment_plan_and_update_status_does_not_change_when_count_below_required(payment_plan):
    service = PaymentPlanService(payment_plan=payment_plan)
    service.action = PaymentPlan.Action.APPROVE.value
    approval_process = MagicMock()
    approval_process.approvals.filter.return_value.count.return_value = 0

    with patch.object(service, "get_required_number_by_approval_type", return_value=5):
        service.check_payment_plan_and_update_status(approval_process)


def test_build_payments_chunks_with_chunks_no_none_returns_single_chunk(payment_plan_with_payments):
    service = PaymentPlanService(payment_plan=payment_plan_with_payments)
    payments = payment_plan_with_payments.eligible_payments.all()
    payments_count = payments.count()

    with patch.object(service, "_validate_split_by_record"):
        result = service._build_payments_chunks(
            split_type=PaymentPlanSplit.SplitType.BY_RECORDS,
            chunks_no=None,
            payments=payments,
            payments_count=payments_count,
        )
    assert len(result) == 1
