from typing import Any, Callable

import pytest
from rest_framework import status
from rest_framework.reverse import reverse

from extras.test_utils.factories import (
    BusinessAreaFactory,
    CurrencyFactory,
    PaymentFactory,
    PaymentPlanFactory,
    PaymentPlanPurposeFactory,
    ProgramCycleFactory,
    ProgramFactory,
    UserFactory,
)
from hope.apps.account.permissions import Permissions
from hope.models import Payment, PaymentPlan, PaymentPlanGroup, Program

pytestmark = pytest.mark.django_db


@pytest.fixture
def accepted_pp_context(api_client: Callable, create_user_role_with_permissions: Any) -> dict[str, Any]:
    business_area = BusinessAreaFactory(slug="afghanistan")
    user = UserFactory()
    program = ProgramFactory(business_area=business_area, status=Program.ACTIVE)
    cycle = ProgramCycleFactory(program=program)
    currency = CurrencyFactory(code="PLN", name="Polish Zloty")
    payment_plan = PaymentPlanFactory(
        name="Standard PP",
        business_area=business_area,
        program_cycle=cycle,
        plan_type=PaymentPlan.PlanType.REGULAR,
        status=PaymentPlan.Status.ACCEPTED,
        currency=currency,
    )
    payment_plan.payment_plan_purposes.add(PaymentPlanPurposeFactory())
    payment_plan_group = payment_plan.payment_plan_group
    payment_plan_group.status = PaymentPlanGroup.Status.ACCEPTED
    payment_plan_group.save(update_fields=["status"])
    create_user_role_with_permissions(user, [Permissions.PM_PAYMENT_PLAN_GROUP_VIEW_DETAIL], business_area, program)
    return {
        "payment_plan": payment_plan,
        "client": api_client(user),
        "url": reverse(
            "api:payments:payment-plan-groups-detail",
            kwargs={
                "business_area_slug": business_area.slug,
                "program_code": program.code,
                "pk": payment_plan_group.pk,
            },
        ),
    }


@pytest.mark.parametrize(
    "payment_status",
    [Payment.STATUS_PENDING, Payment.STATUS_SENT_TO_PG, Payment.STATUS_SENT_TO_FSP],
)
def test_can_create_top_up_arrange_only_pending_payments_act_get_group_detail_assert_true(
    accepted_pp_context: dict[str, Any],
    payment_status: str,
) -> None:
    PaymentFactory(parent=accepted_pp_context["payment_plan"], status=payment_status)
    PaymentFactory(parent=accepted_pp_context["payment_plan"], status=payment_status)

    response = accepted_pp_context["client"].get(accepted_pp_context["url"])

    assert response.status_code == status.HTTP_200_OK
    assert accepted_pp_context["payment_plan"].eligible_payments_for_top_up().count() == 2
    assert response.json()["can_create_top_up"] is True
