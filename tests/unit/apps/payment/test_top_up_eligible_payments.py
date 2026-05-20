import pytest

from extras.test_utils.factories.household import HouseholdFactory
from extras.test_utils.factories.payment import PaymentFactory, PaymentPlanFactory
from hope.models import Payment, PaymentPlan


@pytest.fixture
def regular_pp(db):
    return PaymentPlanFactory(plan_type=PaymentPlan.PlanType.REGULAR)


@pytest.fixture
def delivered_payment(regular_pp):
    return PaymentFactory(parent=regular_pp, status=Payment.STATUS_DISTRIBUTION_SUCCESS)


@pytest.fixture
def pending_payment(regular_pp):
    return PaymentFactory(parent=regular_pp, status=Payment.STATUS_PENDING)


@pytest.fixture
def failed_payment(regular_pp):
    return PaymentFactory(parent=regular_pp, status=Payment.STATUS_FORCE_FAILED)


@pytest.fixture
def withdrawn_delivered_payment(regular_pp):
    household = HouseholdFactory(
        business_area=regular_pp.business_area,
        program=regular_pp.program_cycle.program,
        withdrawn=True,
    )
    return PaymentFactory(
        parent=regular_pp,
        household=household,
        status=Payment.STATUS_DISTRIBUTION_SUCCESS,
    )


def test_eligible_payments_arrange_delivered_act_query_assert_included(regular_pp, delivered_payment):
    eligible = regular_pp.eligible_payments_for_top_up()

    assert list(eligible.values_list("id", flat=True)) == [delivered_payment.id]


def test_eligible_payments_arrange_pending_act_query_assert_included(regular_pp, pending_payment):
    eligible = regular_pp.eligible_payments_for_top_up()

    assert list(eligible.values_list("id", flat=True)) == [pending_payment.id]


def test_eligible_payments_arrange_failed_act_query_assert_excluded(regular_pp, failed_payment):
    eligible = regular_pp.eligible_payments_for_top_up()

    assert not eligible.exists()


def test_eligible_payments_arrange_withdrawn_household_act_query_assert_excluded(
    regular_pp, withdrawn_delivered_payment
):
    eligible = regular_pp.eligible_payments_for_top_up()

    assert not eligible.exists()


def test_eligible_payments_arrange_existing_topup_act_query_assert_beneficiary_excluded(regular_pp, delivered_payment):
    top_up_pp = PaymentPlanFactory(
        plan_type=PaymentPlan.PlanType.TOP_UP,
        source_payment_plan=regular_pp,
        program_cycle=regular_pp.program_cycle,
    )
    PaymentFactory(
        parent=top_up_pp,
        household=delivered_payment.household,
        status=Payment.STATUS_PENDING,
    )

    eligible = regular_pp.eligible_payments_for_top_up()

    assert not eligible.exists()


def test_eligible_payments_arrange_no_payments_act_query_assert_empty(regular_pp):
    eligible = regular_pp.eligible_payments_for_top_up()

    assert not eligible.exists()


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
def test_eligible_payments_parametrized_by_status_act_query_assert_included(regular_pp, delivered_status):
    payment = PaymentFactory(parent=regular_pp, status=delivered_status)

    eligible = regular_pp.eligible_payments_for_top_up()

    assert list(eligible.values_list("id", flat=True)) == [payment.id]


@pytest.mark.parametrize(
    "failed_status",
    [
        Payment.STATUS_FORCE_FAILED,
        Payment.STATUS_ERROR,
        Payment.STATUS_MANUALLY_CANCELLED,
        Payment.STATUS_NOT_DISTRIBUTED,
    ],
)
def test_eligible_payments_parametrized_by_failed_status_act_query_assert_excluded(regular_pp, failed_status):
    PaymentFactory(parent=regular_pp, status=failed_status)

    eligible = regular_pp.eligible_payments_for_top_up()

    assert not eligible.exists()


def test_eligible_payments_query_count_stays_within_budget(regular_pp, django_assert_num_queries):
    PaymentFactory(parent=regular_pp, status=Payment.STATUS_DISTRIBUTION_SUCCESS)
    PaymentFactory(parent=regular_pp, status=Payment.STATUS_PENDING)

    with django_assert_num_queries(1):
        assert list(regular_pp.eligible_payments_for_top_up().values_list("id", flat=True))
