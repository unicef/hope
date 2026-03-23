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


def test_build_payments_chunks_raises_value_error_when_chunks_no_is_none(payment_plan_with_payments):
    service = PaymentPlanService(payment_plan=payment_plan_with_payments)
    payments = payment_plan_with_payments.eligible_payments.all()
    payments_count = payments.count()

    with patch.object(service, "_validate_split_by_record"):
        with pytest.raises(ValueError, match="chunks_no must not be None for BY_RECORDS split"):
            service._build_payments_chunks(
                split_type=PaymentPlanSplit.SplitType.BY_RECORDS,
                chunks_no=None,
                payments=payments,
                payments_count=payments_count,
            )
