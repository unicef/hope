from typing import Any, Callable

import pytest
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.reverse import reverse

from extras.test_utils.factories import (
    BusinessAreaFactory,
    PartnerFactory,
    PaymentFactory,
    PaymentPlanFactory,
    ProgramCycleFactory,
    ProgramFactory,
    UserFactory,
)
from hope.apps.account.permissions import Permissions
from hope.apps.payment.services.payment_plan_services import PaymentPlanService
from hope.models import Payment, PaymentPlan, Program, ProgramCycle, User

pytestmark = pytest.mark.django_db


@pytest.fixture
def business_area() -> Any:
    return BusinessAreaFactory(slug="afghanistan")


@pytest.fixture
def user() -> User:
    return UserFactory()


@pytest.fixture
def program(business_area: Any) -> Program:
    return ProgramFactory(status=Program.ACTIVE, business_area=business_area, cycle=False)


@pytest.fixture
def cycle(program: Program) -> ProgramCycle:
    return ProgramCycleFactory(status=ProgramCycle.ACTIVE, program=program)


@pytest.fixture
def source_plan(user: User, business_area: Any, cycle: ProgramCycle) -> PaymentPlan:
    return PaymentPlanFactory(
        program_cycle=cycle,
        created_by=user,
        business_area=business_area,
        status=PaymentPlan.Status.ACCEPTED,
    )


@pytest.fixture
def source_payment(source_plan: PaymentPlan) -> Payment:
    return PaymentFactory(parent=source_plan)


@pytest.fixture
def top_up(source_plan: PaymentPlan) -> PaymentPlan:
    return PaymentPlanFactory(
        program_cycle=source_plan.program_cycle,
        created_by=source_plan.created_by,
        business_area=source_plan.business_area,
        status=PaymentPlan.Status.OPEN,
        plan_type=PaymentPlan.PlanType.TOP_UP,
        source_payment_plan=source_plan,
    )


@pytest.fixture
def top_up_payment(top_up: PaymentPlan, source_payment: Payment) -> Payment:
    return PaymentFactory(parent=top_up, household=source_payment.household)


@pytest.fixture
def follow_up(source_plan: PaymentPlan) -> PaymentPlan:
    return PaymentPlanFactory(
        program_cycle=source_plan.program_cycle,
        created_by=source_plan.created_by,
        business_area=source_plan.business_area,
        status=PaymentPlan.Status.OPEN,
        plan_type=PaymentPlan.PlanType.FOLLOW_UP,
        source_payment_plan=source_plan,
    )


@pytest.fixture
def failed_source_payment(source_payment: Payment) -> Payment:
    source_payment.status = Payment.STATUS_ERROR
    source_payment.save(update_fields=["status"])
    return source_payment


@pytest.fixture
def follow_up_payment(follow_up: PaymentPlan, failed_source_payment: Payment) -> Payment:
    return PaymentFactory(
        parent=follow_up,
        household=failed_source_payment.household,
        source_payment=failed_source_payment,
        is_follow_up=True,
    )


@pytest.fixture
def amendment(top_up: PaymentPlan) -> PaymentPlan:
    return PaymentPlanFactory(
        program_cycle=top_up.program_cycle,
        created_by=top_up.created_by,
        business_area=top_up.business_area,
        status=PaymentPlan.Status.OPEN,
        plan_type=PaymentPlan.PlanType.TOP_UP_AMENDMENT,
        source_payment_plan=top_up,
    )


@pytest.fixture
def amendment_payment(amendment: PaymentPlan, top_up_payment: Payment) -> Payment:
    return PaymentFactory(parent=amendment, household=top_up_payment.household)


@pytest.fixture
def newer_top_up(top_up: PaymentPlan, source_plan: PaymentPlan) -> PaymentPlan:
    return PaymentPlanFactory(
        program_cycle=source_plan.program_cycle,
        created_by=source_plan.created_by,
        business_area=source_plan.business_area,
        status=PaymentPlan.Status.OPEN,
        plan_type=PaymentPlan.PlanType.TOP_UP,
        source_payment_plan=source_plan,
    )


def test_delete_top_up_soft_deletes_plan_and_payments(top_up: PaymentPlan, top_up_payment: Payment) -> None:
    deleted = PaymentPlanService(payment_plan=top_up).delete()

    assert deleted.is_removed is True
    assert deleted.status == PaymentPlan.Status.OPEN
    assert not PaymentPlan.objects.filter(pk=top_up.pk).exists()
    assert not Payment.objects.filter(pk=top_up_payment.pk).exists()
    assert Payment.all_objects.get(pk=top_up_payment.pk).is_removed is True


def test_delete_top_up_keeps_cycle_status(top_up: PaymentPlan, cycle: ProgramCycle) -> None:
    PaymentPlanService(payment_plan=top_up).delete()

    cycle.refresh_from_db()
    assert cycle.status == ProgramCycle.ACTIVE


def test_delete_top_up_restores_top_up_eligibility(
    source_plan: PaymentPlan, source_payment: Payment, top_up: PaymentPlan, top_up_payment: Payment
) -> None:
    assert not source_plan.eligible_payments_for_top_up().filter(pk=source_payment.pk).exists()

    PaymentPlanService(payment_plan=top_up).delete()

    assert source_plan.eligible_payments_for_top_up().filter(pk=source_payment.pk).exists()
    assert source_plan.can_create_top_up is True


def test_delete_follow_up_soft_deletes_plan_and_payments(follow_up: PaymentPlan, follow_up_payment: Payment) -> None:
    deleted = PaymentPlanService(payment_plan=follow_up).delete()

    assert deleted.is_removed is True
    assert not PaymentPlan.objects.filter(pk=follow_up.pk).exists()
    assert Payment.all_objects.get(pk=follow_up_payment.pk).is_removed is True


def test_delete_follow_up_restores_follow_up_pool(
    source_plan: PaymentPlan,
    failed_source_payment: Payment,
    follow_up: PaymentPlan,
    follow_up_payment: Payment,
) -> None:
    assert not source_plan.unsuccessful_payments_for_follow_up().filter(pk=failed_source_payment.pk).exists()

    PaymentPlanService(payment_plan=follow_up).delete()

    assert source_plan.unsuccessful_payments_for_follow_up().filter(pk=failed_source_payment.pk).exists()


def test_delete_amendment_soft_deletes_plan_and_payments(amendment: PaymentPlan, amendment_payment: Payment) -> None:
    deleted = PaymentPlanService(payment_plan=amendment).delete()

    assert deleted.is_removed is True
    assert not PaymentPlan.objects.filter(pk=amendment.pk).exists()
    assert Payment.all_objects.get(pk=amendment_payment.pk).is_removed is True


def test_delete_amendment_restores_amendment_pool(
    top_up: PaymentPlan,
    top_up_payment: Payment,
    amendment: PaymentPlan,
    amendment_payment: Payment,
) -> None:
    assert not top_up.eligible_payments_for_top_up_amendment().filter(pk=top_up_payment.pk).exists()

    PaymentPlanService(payment_plan=amendment).delete()

    assert top_up.eligible_payments_for_top_up_amendment().filter(pk=top_up_payment.pk).exists()


def test_delete_older_top_up_with_newer_active_raises(top_up: PaymentPlan, newer_top_up: PaymentPlan) -> None:
    with pytest.raises(ValidationError) as error:
        PaymentPlanService(payment_plan=top_up).delete()

    assert "Only the most recent Top Up" in str(error.value)
    assert PaymentPlan.objects.filter(pk=top_up.pk).exists()


def test_delete_newest_top_up_when_older_already_removed(top_up: PaymentPlan, newer_top_up: PaymentPlan) -> None:
    top_up.delete()

    deleted = PaymentPlanService(payment_plan=newer_top_up).delete()

    assert deleted.is_removed is True


def test_delete_follow_up_not_blocked_by_newer_top_up(follow_up: PaymentPlan, newer_top_up: PaymentPlan) -> None:
    deleted = PaymentPlanService(payment_plan=follow_up).delete()

    assert deleted.is_removed is True
    assert PaymentPlan.objects.filter(pk=newer_top_up.pk).exists()


def test_delete_child_plan_wrong_status_raises(top_up: PaymentPlan) -> None:
    top_up.status = PaymentPlan.Status.LOCKED
    top_up.save(update_fields=["status"])

    with pytest.raises(ValidationError) as error:
        PaymentPlanService(payment_plan=top_up).delete()

    assert error.value.detail[0] == "Deletion is only allowed when the status is 'Open'"


def test_delete_top_up_query_count(
    top_up: PaymentPlan, top_up_payment: Payment, django_assert_num_queries: Callable
) -> None:
    with django_assert_num_queries(9):
        PaymentPlanService(payment_plan=top_up).delete()


def test_destroy_top_up_via_api(
    api_client: Callable,
    create_user_role_with_permissions: Any,
    business_area: Any,
    program: Program,
    top_up: PaymentPlan,
    top_up_payment: Payment,
) -> None:
    partner = PartnerFactory(name="unittest")
    api_user = UserFactory(partner=partner)
    create_user_role_with_permissions(api_user, [Permissions.PM_CREATE], business_area, program)
    client = api_client(api_user)
    url = reverse(
        "api:payments:payment-plans-detail",
        kwargs={
            "business_area_slug": business_area.slug,
            "program_code": program.code,
            "pk": str(top_up.pk),
        },
    )

    response = client.delete(url)

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not PaymentPlan.objects.filter(pk=top_up.pk).exists()
    assert not Payment.objects.filter(pk=top_up_payment.pk).exists()
