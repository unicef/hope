"""Exhaustive coverage of payment-plan conflict detection across plan types.

`PaymentQuerySet.with_payment_plan_conflicts` flags a payment as conflicted when
another payment in the same program cycle covers the same household under a plan
that shares at least one purpose. The TopUp/Amendment feature adds the rule that
conflicts only ever arise between plans of the **same** ``plan_type`` — a TopUp is
by design an extra payment to households already paid by its source plan, so it
must not conflict with that Standard plan, nor an Amendment with its TopUp. Two
*different* TopUps for the same purpose in a cycle still conflict.

These tests pin down that rule together with every other dimension that gates a
conflict: cycle, household, shared purpose, plan/payment status, soft-deletion
and the already-``conflicted`` flag.
"""

import json
from typing import Any

import pytest

from extras.test_utils.factories.core import PaymentPlanPurposeFactory
from extras.test_utils.factories.payment import PaymentFactory, PaymentPlanFactory
from extras.test_utils.factories.program import ProgramCycleFactory, ProgramFactory
from hope.models import Payment, PaymentPlan

pytestmark = pytest.mark.django_db

PlanType = PaymentPlan.PlanType
Status = PaymentPlan.Status

ALL_PLAN_TYPES = [
    PlanType.REGULAR,
    PlanType.TOP_UP,
    PlanType.TOP_UP_AMENDMENT,
    PlanType.FOLLOW_UP,
]
DIFFERENT_TYPE_PAIRS = [(q, c) for q in ALL_PLAN_TYPES for c in ALL_PLAN_TYPES if q != c]

# A scenario builds a queried plan and a single candidate "conflicting" plan, each
# with one payment. Every knob below has a default that produces a soft conflict;
# each test overrides only the knobs it exercises plus the expected flags.
DEFAULT_SCENARIO: dict[str, Any] = {
    "queried_type": PlanType.TOP_UP,
    "queried_status": Status.OPEN,
    "conflicting_type": PlanType.TOP_UP,
    "conflicting_status": Status.OPEN,
    "same_cycle": True,
    "same_household": True,
    "share_purpose": True,
    "conflicting_payment_status": Payment.STATUS_DISTRIBUTION_SUCCESS,
    "conflicting_plan_removed": False,
    "conflicting_payment_conflicted": False,
    "expect_soft": True,
    "expect_hard": False,
}


@pytest.fixture
def conflict_scenario(request: Any, db: Any) -> tuple[PaymentPlan, Any, bool, bool]:
    spec: dict[str, Any] = {**DEFAULT_SCENARIO, **request.param}

    purpose = PaymentPlanPurposeFactory()
    other_purpose = PaymentPlanPurposeFactory()
    program = ProgramFactory(status="ACTIVE")
    program.payment_plan_purposes.set([purpose, other_purpose])
    cycle = ProgramCycleFactory(program=program)
    other_cycle = ProgramCycleFactory(program=program)

    queried_plan = PaymentPlanFactory(
        program_cycle=cycle,
        plan_type=spec["queried_type"],
        status=spec["queried_status"],
    )
    queried_plan.payment_plan_purposes.add(purpose)

    conflicting_plan = PaymentPlanFactory(
        program_cycle=cycle if spec["same_cycle"] else other_cycle,
        business_area=queried_plan.business_area,
        plan_type=spec["conflicting_type"],
        status=spec["conflicting_status"],
        is_removed=spec["conflicting_plan_removed"],
    )
    conflicting_plan.payment_plan_purposes.add(purpose if spec["share_purpose"] else other_purpose)

    queried_payment = PaymentFactory(parent=queried_plan, status=Payment.STATUS_DISTRIBUTION_SUCCESS)
    conflicting_kwargs: dict[str, Any] = {
        "parent": conflicting_plan,
        "status": spec["conflicting_payment_status"],
        "conflicted": spec["conflicting_payment_conflicted"],
    }
    if spec["same_household"]:
        conflicting_kwargs["household"] = queried_payment.household
    PaymentFactory(**conflicting_kwargs)

    return queried_plan, queried_payment.id, spec["expect_soft"], spec["expect_hard"]


@pytest.mark.parametrize(
    "conflict_scenario",
    [pytest.param({"queried_type": t, "conflicting_type": t}, id=f"soft-{t.value}") for t in ALL_PLAN_TYPES]
    + [
        pytest.param(
            {
                "queried_type": t,
                "conflicting_type": t,
                "conflicting_status": Status.LOCKED,
                "expect_soft": False,
                "expect_hard": True,
            },
            id=f"hard-{t.value}",
        )
        for t in ALL_PLAN_TYPES
    ],
    indirect=True,
)
def test_conflict_detected_between_plans_of_the_same_type(
    conflict_scenario: tuple[PaymentPlan, Any, bool, bool], django_assert_num_queries: Any
) -> None:
    plan, payment_id, expect_soft, expect_hard = conflict_scenario

    with django_assert_num_queries(1):
        result = plan.eligible_payments_with_conflicts.filter(id=payment_id).values()[0]

    assert result["payment_plan_soft_conflicted"] is expect_soft
    assert result["payment_plan_hard_conflicted"] is expect_hard


@pytest.mark.parametrize(
    "conflict_scenario",
    [
        pytest.param(
            {"conflicting_status": status, "expect_soft": False, "expect_hard": True},
            id=status.value,
        )
        for status in PaymentPlan.HARD_CONFLICT_STATUSES
    ],
    indirect=True,
)
def test_hard_conflict_detected_for_every_hard_conflict_status(
    conflict_scenario: tuple[PaymentPlan, Any, bool, bool], django_assert_num_queries: Any
) -> None:
    plan, payment_id, expect_soft, expect_hard = conflict_scenario

    with django_assert_num_queries(1):
        result = plan.eligible_payments_with_conflicts.filter(id=payment_id).values()[0]

    assert result["payment_plan_soft_conflicted"] is expect_soft
    assert result["payment_plan_hard_conflicted"] is expect_hard


@pytest.mark.parametrize(
    "conflict_scenario",
    [
        pytest.param(
            {"queried_type": q, "conflicting_type": c, "expect_soft": False, "expect_hard": False},
            id=f"soft-{q.value}-vs-{c.value}",
        )
        for q, c in DIFFERENT_TYPE_PAIRS
    ]
    + [
        pytest.param(
            {
                "queried_type": q,
                "conflicting_type": c,
                "conflicting_status": Status.LOCKED,
                "expect_soft": False,
                "expect_hard": False,
            },
            id=f"hard-{q.value}-vs-{c.value}",
        )
        for q, c in DIFFERENT_TYPE_PAIRS
    ],
    indirect=True,
)
def test_no_conflict_between_plans_of_different_types(
    conflict_scenario: tuple[PaymentPlan, Any, bool, bool], django_assert_num_queries: Any
) -> None:
    plan, payment_id, expect_soft, expect_hard = conflict_scenario

    with django_assert_num_queries(1):
        result = plan.eligible_payments_with_conflicts.filter(id=payment_id).values()[0]

    assert result["payment_plan_soft_conflicted"] is expect_soft
    assert result["payment_plan_hard_conflicted"] is expect_hard


@pytest.mark.parametrize(
    "conflict_scenario",
    [
        pytest.param(
            {"same_cycle": False, "expect_soft": False, "expect_hard": False},
            id="different-cycle",
        ),
        pytest.param(
            {"same_household": False, "expect_soft": False, "expect_hard": False},
            id="different-household",
        ),
        pytest.param(
            {"share_purpose": False, "expect_soft": False, "expect_hard": False},
            id="no-shared-purpose",
        ),
        pytest.param(
            {"conflicting_plan_removed": True, "expect_soft": False, "expect_hard": False},
            id="conflicting-plan-soft-deleted",
        ),
        pytest.param(
            {"conflicting_status": Status.ABORTED, "expect_soft": False, "expect_hard": False},
            id="conflicting-plan-aborted",
        ),
        pytest.param(
            {"conflicting_payment_conflicted": True, "expect_soft": False, "expect_hard": False},
            id="soft-candidate-already-conflicted",
        ),
        pytest.param(
            {
                "conflicting_status": Status.LOCKED,
                "conflicting_payment_conflicted": True,
                "expect_soft": False,
                "expect_hard": False,
            },
            id="hard-candidate-already-conflicted",
        ),
    ]
    + [
        pytest.param(
            {"conflicting_payment_status": status, "expect_soft": False, "expect_hard": False},
            id=f"conflicting-payment-failed-{status}",
        )
        for status in Payment.FAILED_STATUSES
    ],
    indirect=True,
)
def test_no_conflict_when_scope_or_payment_state_excludes_candidate(
    conflict_scenario: tuple[PaymentPlan, Any, bool, bool], django_assert_num_queries: Any
) -> None:
    plan, payment_id, expect_soft, expect_hard = conflict_scenario

    with django_assert_num_queries(1):
        result = plan.eligible_payments_with_conflicts.filter(id=payment_id).values()[0]

    assert result["payment_plan_soft_conflicted"] is expect_soft
    assert result["payment_plan_hard_conflicted"] is expect_hard


@pytest.mark.parametrize(
    "conflict_scenario",
    [
        pytest.param(
            {
                "queried_status": status,
                "conflicting_status": Status.LOCKED,
                "expect_soft": False,
                "expect_hard": False,
            },
            id=status.value,
        )
        for status in [Status.LOCKED, Status.ACCEPTED, Status.FINISHED]
    ],
    indirect=True,
)
def test_conflict_flags_default_false_when_queried_plan_not_open(
    conflict_scenario: tuple[PaymentPlan, Any, bool, bool], django_assert_num_queries: Any
) -> None:
    plan, payment_id, expect_soft, expect_hard = conflict_scenario

    with django_assert_num_queries(1):
        result = plan.eligible_payments_with_conflicts.filter(id=payment_id).values()[0]

    assert result["payment_plan_soft_conflicted"] is expect_soft
    assert result["payment_plan_hard_conflicted"] is expect_hard


@pytest.fixture
def soft_conflict_pair(db: Any) -> tuple[PaymentPlan, Any, PaymentPlan, Payment]:
    purpose = PaymentPlanPurposeFactory()
    program = ProgramFactory(status="ACTIVE")
    program.payment_plan_purposes.add(purpose)
    cycle = ProgramCycleFactory(program=program)
    queried = PaymentPlanFactory(program_cycle=cycle, plan_type=PlanType.TOP_UP, status=Status.OPEN)
    queried.payment_plan_purposes.add(purpose)
    conflicting = PaymentPlanFactory(
        program_cycle=cycle,
        business_area=queried.business_area,
        plan_type=PlanType.TOP_UP,
        status=Status.OPEN,
    )
    conflicting.payment_plan_purposes.add(purpose)
    queried_payment = PaymentFactory(parent=queried, status=Payment.STATUS_DISTRIBUTION_SUCCESS)
    conflicting_payment = PaymentFactory(
        parent=conflicting,
        household=queried_payment.household,
        status=Payment.STATUS_DISTRIBUTION_SUCCESS,
    )
    return queried, queried_payment.id, conflicting, conflicting_payment


def test_soft_conflict_data_payload_describes_the_conflicting_plan(
    soft_conflict_pair: tuple[PaymentPlan, Any, PaymentPlan, Payment], django_assert_num_queries: Any
) -> None:
    queried, payment_id, conflicting, conflicting_payment = soft_conflict_pair

    with django_assert_num_queries(1):
        result = queried.eligible_payments_with_conflicts.filter(id=payment_id).values()[0]

    assert result["payment_plan_soft_conflicted"] is True
    assert len(result["payment_plan_soft_conflicted_data"]) == 1
    payload = json.loads(result["payment_plan_soft_conflicted_data"][0])
    assert payload["payment_plan_id"] == str(conflicting.id)
    assert payload["payment_plan_unicef_id"] == str(conflicting.unicef_id)
    assert payload["payment_plan_status"] == str(conflicting.status)
    assert payload["payment_id"] == str(conflicting_payment.id)
    assert payload["payment_unicef_id"] == str(conflicting_payment.unicef_id)


@pytest.fixture
def hard_conflict_pair(db: Any) -> tuple[PaymentPlan, Any, PaymentPlan, Payment]:
    purpose = PaymentPlanPurposeFactory()
    program = ProgramFactory(status="ACTIVE")
    program.payment_plan_purposes.add(purpose)
    cycle = ProgramCycleFactory(program=program)
    queried = PaymentPlanFactory(program_cycle=cycle, plan_type=PlanType.TOP_UP, status=Status.OPEN)
    queried.payment_plan_purposes.add(purpose)
    conflicting = PaymentPlanFactory(
        program_cycle=cycle,
        business_area=queried.business_area,
        plan_type=PlanType.TOP_UP,
        status=Status.LOCKED,
    )
    conflicting.payment_plan_purposes.add(purpose)
    queried_payment = PaymentFactory(parent=queried, status=Payment.STATUS_DISTRIBUTION_SUCCESS)
    conflicting_payment = PaymentFactory(
        parent=conflicting,
        household=queried_payment.household,
        status=Payment.STATUS_DISTRIBUTION_SUCCESS,
    )
    return queried, queried_payment.id, conflicting, conflicting_payment


def test_hard_conflict_data_payload_describes_the_conflicting_plan(
    hard_conflict_pair: tuple[PaymentPlan, Any, PaymentPlan, Payment], django_assert_num_queries: Any
) -> None:
    queried, payment_id, conflicting, conflicting_payment = hard_conflict_pair

    with django_assert_num_queries(1):
        result = queried.eligible_payments_with_conflicts.filter(id=payment_id).values()[0]

    assert result["payment_plan_hard_conflicted"] is True
    assert len(result["payment_plan_hard_conflicted_data"]) == 1
    payload = json.loads(result["payment_plan_hard_conflicted_data"][0])
    assert payload["payment_plan_id"] == str(conflicting.id)
    assert payload["payment_id"] == str(conflicting_payment.id)


@pytest.fixture
def top_up_with_source_and_sibling(db: Any) -> tuple[PaymentPlan, Any, PaymentPlan]:
    """A TopUp whose household appears in both its source Standard plan and a
    second, unrelated TopUp — the source is suppressed, the sibling is not."""
    purpose = PaymentPlanPurposeFactory()
    program = ProgramFactory(status="ACTIVE")
    program.payment_plan_purposes.add(purpose)
    cycle = ProgramCycleFactory(program=program)
    regular = PaymentPlanFactory(program_cycle=cycle, plan_type=PlanType.REGULAR, status=Status.LOCKED)
    regular.payment_plan_purposes.add(purpose)
    top_up = PaymentPlanFactory(
        program_cycle=cycle,
        business_area=regular.business_area,
        plan_type=PlanType.TOP_UP,
        status=Status.OPEN,
        source_payment_plan=regular,
    )
    top_up.payment_plan_purposes.add(purpose)
    sibling_top_up = PaymentPlanFactory(
        program_cycle=cycle,
        business_area=regular.business_area,
        plan_type=PlanType.TOP_UP,
        status=Status.LOCKED,
    )
    sibling_top_up.payment_plan_purposes.add(purpose)
    regular_payment = PaymentFactory(parent=regular, status=Payment.STATUS_DISTRIBUTION_SUCCESS)
    top_up_payment = PaymentFactory(
        parent=top_up,
        household=regular_payment.household,
        status=Payment.STATUS_DISTRIBUTION_SUCCESS,
    )
    PaymentFactory(
        parent=sibling_top_up,
        household=regular_payment.household,
        status=Payment.STATUS_DISTRIBUTION_SUCCESS,
    )
    return top_up, top_up_payment.id, sibling_top_up


def test_top_up_conflict_is_selective_source_suppressed_sibling_top_up_kept(
    top_up_with_source_and_sibling: tuple[PaymentPlan, Any, PaymentPlan], django_assert_num_queries: Any
) -> None:
    top_up, payment_id, sibling_top_up = top_up_with_source_and_sibling

    with django_assert_num_queries(1):
        result = top_up.eligible_payments_with_conflicts.filter(id=payment_id).values()[0]

    assert result["payment_plan_hard_conflicted"] is True
    assert result["payment_plan_soft_conflicted"] is False
    assert len(result["payment_plan_hard_conflicted_data"]) == 1
    payload = json.loads(result["payment_plan_hard_conflicted_data"][0])
    assert payload["payment_plan_id"] == str(sibling_top_up.id)


def test_can_be_locked_false_when_a_sibling_top_up_hard_conflicts(
    top_up_with_source_and_sibling: tuple[PaymentPlan, Any, PaymentPlan], django_assert_num_queries: Any
) -> None:
    top_up, _payment_id, _sibling_top_up = top_up_with_source_and_sibling

    with django_assert_num_queries(1):
        can_be_locked = top_up.can_be_locked

    assert can_be_locked is False


@pytest.fixture
def top_up_overlapping_only_its_source(db: Any) -> PaymentPlan:
    purpose = PaymentPlanPurposeFactory()
    program = ProgramFactory(status="ACTIVE")
    program.payment_plan_purposes.add(purpose)
    cycle = ProgramCycleFactory(program=program)
    regular = PaymentPlanFactory(program_cycle=cycle, plan_type=PlanType.REGULAR, status=Status.LOCKED)
    regular.payment_plan_purposes.add(purpose)
    top_up = PaymentPlanFactory(
        program_cycle=cycle,
        business_area=regular.business_area,
        plan_type=PlanType.TOP_UP,
        status=Status.OPEN,
        source_payment_plan=regular,
    )
    top_up.payment_plan_purposes.add(purpose)
    regular_payment = PaymentFactory(parent=regular, status=Payment.STATUS_DISTRIBUTION_SUCCESS)
    PaymentFactory(
        parent=top_up,
        household=regular_payment.household,
        status=Payment.STATUS_DISTRIBUTION_SUCCESS,
    )
    return top_up


def test_can_be_locked_true_when_the_only_overlap_is_the_suppressed_source_plan(
    top_up_overlapping_only_its_source: PaymentPlan, django_assert_num_queries: Any
) -> None:
    top_up = top_up_overlapping_only_its_source

    with django_assert_num_queries(1):
        can_be_locked = top_up.can_be_locked

    assert can_be_locked is True
