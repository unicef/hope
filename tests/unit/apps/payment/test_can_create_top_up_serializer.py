import pytest

from extras.test_utils.factories.payment import PaymentFactory, PaymentPlanFactory
from hope.apps.payment.api.serializers import PaymentPlanDetailSerializer
from hope.models import Payment, PaymentPlan


def _flag(payment_plan: PaymentPlan) -> bool:
    serializer = PaymentPlanDetailSerializer()
    return serializer.get_can_create_top_up(payment_plan)


@pytest.fixture
def regular_pp(db):
    return PaymentPlanFactory(plan_type=PaymentPlan.PlanType.REGULAR)


@pytest.mark.parametrize(
    "delivered_status",
    [
        Payment.STATUS_SUCCESS,
        Payment.STATUS_DISTRIBUTION_SUCCESS,
        Payment.STATUS_DISTRIBUTION_PARTIAL,
        Payment.STATUS_PENDING,
        Payment.STATUS_SENT_TO_PG,
        Payment.STATUS_SENT_TO_FSP,
    ],
)
def test_can_create_top_up_arrange_regular_with_eligible_status_act_query_assert_true(regular_pp, delivered_status):
    PaymentFactory(parent=regular_pp, status=delivered_status)

    assert _flag(regular_pp) is True


def test_can_create_top_up_arrange_regular_with_no_payments_act_query_assert_false(regular_pp):
    assert _flag(regular_pp) is False


def test_can_create_top_up_arrange_regular_with_only_failed_payments_act_query_assert_false(regular_pp):
    PaymentFactory(parent=regular_pp, status=Payment.STATUS_FORCE_FAILED)

    assert _flag(regular_pp) is False


def test_can_create_top_up_arrange_follow_up_with_eligible_payment_act_query_assert_false(db):
    pp = PaymentPlanFactory(plan_type=PaymentPlan.PlanType.FOLLOW_UP)
    PaymentFactory(parent=pp, status=Payment.STATUS_DISTRIBUTION_SUCCESS)

    assert _flag(pp) is False


def test_can_create_top_up_arrange_top_up_with_eligible_payment_act_query_assert_false(db):
    pp = PaymentPlanFactory(plan_type=PaymentPlan.PlanType.TOP_UP)
    PaymentFactory(parent=pp, status=Payment.STATUS_DISTRIBUTION_SUCCESS)

    assert _flag(pp) is False
