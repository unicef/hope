from typing import Any, Callable

import pytest
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.reverse import reverse

from extras.test_utils.factories import (
    BusinessAreaFactory,
    PartnerFactory,
    PaymentFactory,
    PaymentListFactory,
    ProgramCycleFactory,
    ProgramFactory,
    UserFactory,
)
from hope.apps.account.permissions import Permissions
from hope.apps.payment.services.payment_list_services import PaymentListService
from hope.models import Payment, PaymentList, Program, ProgramCycle, User

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
def source_plan(user: User, business_area: Any, cycle: ProgramCycle) -> PaymentList:
    return PaymentListFactory(
        program_cycle=cycle,
        created_by=user,
        business_area=business_area,
        status=PaymentList.Status.ACCEPTED,
    )


@pytest.fixture
def source_payment(source_plan: PaymentList) -> Payment:
    return PaymentFactory(parent=source_plan)


@pytest.fixture
def top_up(source_plan: PaymentList) -> PaymentList:
    return PaymentListFactory(
        program_cycle=source_plan.program_cycle,
        created_by=source_plan.created_by,
        business_area=source_plan.business_area,
        status=PaymentList.Status.OPEN,
        plan_type=PaymentList.PlanType.TOP_UP,
        source_payment_list=source_plan,
    )


@pytest.fixture
def top_up_payment(top_up: PaymentList, source_payment: Payment) -> Payment:
    return PaymentFactory(parent=top_up, household=source_payment.household)


@pytest.fixture
def follow_up(source_plan: PaymentList) -> PaymentList:
    return PaymentListFactory(
        program_cycle=source_plan.program_cycle,
        created_by=source_plan.created_by,
        business_area=source_plan.business_area,
        status=PaymentList.Status.OPEN,
        plan_type=PaymentList.PlanType.FOLLOW_UP,
        source_payment_list=source_plan,
    )


@pytest.fixture
def failed_source_payment(source_payment: Payment) -> Payment:
    source_payment.status = Payment.STATUS_ERROR
    source_payment.save(update_fields=["status"])
    return source_payment


@pytest.fixture
def follow_up_payment(follow_up: PaymentList, failed_source_payment: Payment) -> Payment:
    return PaymentFactory(
        parent=follow_up,
        household=failed_source_payment.household,
        source_payment=failed_source_payment,
        is_follow_up=True,
    )


@pytest.fixture
def amendment(top_up: PaymentList) -> PaymentList:
    return PaymentListFactory(
        program_cycle=top_up.program_cycle,
        created_by=top_up.created_by,
        business_area=top_up.business_area,
        status=PaymentList.Status.OPEN,
        plan_type=PaymentList.PlanType.TOP_UP_AMENDMENT,
        source_payment_list=top_up,
    )


@pytest.fixture
def amendment_payment(amendment: PaymentList, top_up_payment: Payment) -> Payment:
    return PaymentFactory(parent=amendment, household=top_up_payment.household)


@pytest.fixture
def open_regular_plan(user: User, business_area: Any, cycle: ProgramCycle) -> PaymentList:
    return PaymentListFactory(
        program_cycle=cycle,
        created_by=user,
        business_area=business_area,
        status=PaymentList.Status.OPEN,
    )


@pytest.fixture
def newer_top_up(top_up: PaymentList, source_plan: PaymentList) -> PaymentList:
    return PaymentListFactory(
        program_cycle=source_plan.program_cycle,
        created_by=source_plan.created_by,
        business_area=source_plan.business_area,
        status=PaymentList.Status.OPEN,
        plan_type=PaymentList.PlanType.TOP_UP,
        source_payment_list=source_plan,
    )


def test_delete_top_up_soft_deletes_plan_and_payments(top_up: PaymentList, top_up_payment: Payment) -> None:
    deleted = PaymentListService(payment_list=top_up).delete()

    assert deleted.is_removed is True
    assert deleted.status == PaymentList.Status.OPEN
    assert not PaymentList.objects.filter(pk=top_up.pk).exists()
    assert not Payment.objects.filter(pk=top_up_payment.pk).exists()
    assert Payment.all_objects.get(pk=top_up_payment.pk).is_removed is True


def test_delete_top_up_keeps_cycle_status(top_up: PaymentList, cycle: ProgramCycle) -> None:
    PaymentListService(payment_list=top_up).delete()

    cycle.refresh_from_db()
    assert cycle.status == ProgramCycle.ACTIVE


def test_delete_top_up_restores_top_up_eligibility(
    source_plan: PaymentList, source_payment: Payment, top_up: PaymentList, top_up_payment: Payment
) -> None:
    assert not source_plan.eligible_payments_for_top_up().filter(pk=source_payment.pk).exists()

    PaymentListService(payment_list=top_up).delete()

    assert source_plan.eligible_payments_for_top_up().filter(pk=source_payment.pk).exists()


def test_delete_follow_up_soft_deletes_plan_and_payments(follow_up: PaymentList, follow_up_payment: Payment) -> None:
    deleted = PaymentListService(payment_list=follow_up).delete()

    assert deleted.is_removed is True
    assert not PaymentList.objects.filter(pk=follow_up.pk).exists()
    assert Payment.all_objects.get(pk=follow_up_payment.pk).is_removed is True


def test_delete_follow_up_restores_follow_up_pool(
    source_plan: PaymentList,
    failed_source_payment: Payment,
    follow_up: PaymentList,
    follow_up_payment: Payment,
) -> None:
    assert not source_plan.unsuccessful_payments_for_follow_up().filter(pk=failed_source_payment.pk).exists()

    PaymentListService(payment_list=follow_up).delete()

    assert source_plan.unsuccessful_payments_for_follow_up().filter(pk=failed_source_payment.pk).exists()


def test_delete_amendment_soft_deletes_plan_and_payments(amendment: PaymentList, amendment_payment: Payment) -> None:
    deleted = PaymentListService(payment_list=amendment).delete()

    assert deleted.is_removed is True
    assert not PaymentList.objects.filter(pk=amendment.pk).exists()
    assert Payment.all_objects.get(pk=amendment_payment.pk).is_removed is True


def test_delete_amendment_restores_amendment_pool(
    top_up: PaymentList,
    top_up_payment: Payment,
    amendment: PaymentList,
    amendment_payment: Payment,
) -> None:
    assert not top_up.eligible_payments_for_top_up_amendment().filter(pk=top_up_payment.pk).exists()

    PaymentListService(payment_list=amendment).delete()

    assert top_up.eligible_payments_for_top_up_amendment().filter(pk=top_up_payment.pk).exists()


def test_delete_older_top_up_with_newer_active_raises(top_up: PaymentList, newer_top_up: PaymentList) -> None:
    with pytest.raises(ValidationError) as error:
        PaymentListService(payment_list=top_up).delete()

    assert "Only the most recent Top Up" in str(error.value)
    assert PaymentList.objects.filter(pk=top_up.pk).exists()


def test_delete_newest_top_up_when_older_already_removed(top_up: PaymentList, newer_top_up: PaymentList) -> None:
    top_up.delete()

    deleted = PaymentListService(payment_list=newer_top_up).delete()

    assert deleted.is_removed is True


def test_delete_follow_up_not_blocked_by_newer_top_up(follow_up: PaymentList, newer_top_up: PaymentList) -> None:
    deleted = PaymentListService(payment_list=follow_up).delete()

    assert deleted.is_removed is True
    assert PaymentList.objects.filter(pk=newer_top_up.pk).exists()


def test_delete_child_plan_wrong_status_raises(top_up: PaymentList) -> None:
    top_up.status = PaymentList.Status.LOCKED
    top_up.save(update_fields=["status"])

    with pytest.raises(ValidationError) as error:
        PaymentListService(payment_list=top_up).delete()

    assert error.value.detail[0] == "Deletion is only allowed when the status is 'Open'"


def test_can_delete_true_for_newest_top_up(top_up: PaymentList) -> None:
    assert top_up.can_delete is True


def test_can_delete_false_for_top_up_with_newer_sibling(top_up: PaymentList, newer_top_up: PaymentList) -> None:
    assert top_up.can_delete is False
    assert newer_top_up.can_delete is True


def test_can_delete_true_for_open_regular_plan(open_regular_plan: PaymentList) -> None:
    assert open_regular_plan.can_delete is True


def test_can_delete_false_for_non_open_status(source_plan: PaymentList) -> None:
    assert source_plan.can_delete is False


def test_delete_top_up_query_count(
    top_up: PaymentList, top_up_payment: Payment, django_assert_num_queries: Callable
) -> None:
    with django_assert_num_queries(10):
        PaymentListService(payment_list=top_up).delete()


def test_destroy_top_up_via_api(
    api_client: Callable,
    create_user_role_with_permissions: Any,
    business_area: Any,
    program: Program,
    top_up: PaymentList,
    top_up_payment: Payment,
) -> None:
    partner = PartnerFactory(name="unittest")
    api_user = UserFactory(partner=partner)
    create_user_role_with_permissions(api_user, [Permissions.PM_CREATE], business_area, program)
    client = api_client(api_user)
    url = reverse(
        "api:payments:payment-lists-detail",
        kwargs={
            "business_area_slug": business_area.slug,
            "program_code": program.code,
            "pk": str(top_up.pk),
        },
    )

    response = client.delete(url)

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not PaymentList.objects.filter(pk=top_up.pk).exists()
    assert not Payment.objects.filter(pk=top_up_payment.pk).exists()
