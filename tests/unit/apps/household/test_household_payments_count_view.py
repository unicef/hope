from typing import Any

import pytest
from rest_framework import status
from rest_framework.reverse import reverse

from extras.test_utils.factories import (
    BusinessAreaFactory,
    HouseholdFactory,
    PartnerFactory,
    PaymentFactory,
    PaymentPlanFactory,
    ProgramFactory,
    UserFactory,
)
from hope.apps.account.permissions import Permissions
from hope.models import PaymentPlan, Program

pytestmark = pytest.mark.django_db


URL_NAME = "api:households:households-payments-count"


@pytest.fixture
def payments_count_context(api_client: Any) -> dict[str, Any]:
    afghanistan = BusinessAreaFactory(slug="afghanistan", name="Afghanistan")
    program = ProgramFactory(business_area=afghanistan, status=Program.ACTIVE)

    partner = PartnerFactory(name="TestPartner")
    user = UserFactory(partner=partner)
    client = api_client(user)

    household = HouseholdFactory(program=program, business_area=afghanistan)

    return {
        "afghanistan": afghanistan,
        "program": program,
        "user": user,
        "api_client": client,
        "household": household,
    }


def _count_url(ctx: dict[str, Any]) -> str:
    return reverse(
        URL_NAME,
        kwargs={
            "business_area_slug": ctx["afghanistan"].slug,
            "program_code": ctx["program"].code,
            "pk": str(ctx["household"].id),
        },
    )


def _make_payment(ctx: dict[str, Any], pp_status: str, **payment_kwargs: Any) -> None:
    plan = PaymentPlanFactory(
        status=pp_status,
        program_cycle__program=ctx["program"],
        business_area=ctx["afghanistan"],
    )
    PaymentFactory(
        parent=plan,
        household=ctx["household"],
        business_area=ctx["afghanistan"],
        currency=ctx["household"].currency,
        **payment_kwargs,
    )


@pytest.mark.parametrize(
    ("permissions", "expected_status"),
    [
        ([Permissions.POPULATION_VIEW_HOUSEHOLDS_DETAILS], status.HTTP_200_OK),
        ([Permissions.PM_VIEW_DETAILS], status.HTTP_200_OK),
        ([], status.HTTP_403_FORBIDDEN),
    ],
)
def test_household_payments_count_permissions(
    permissions: list,
    expected_status: int,
    create_user_role_with_permissions: Any,
    payments_count_context: dict[str, Any],
) -> None:
    create_user_role_with_permissions(
        user=payments_count_context["user"],
        permissions=permissions,
        business_area=payments_count_context["afghanistan"],
        program=payments_count_context["program"],
    )
    response = payments_count_context["api_client"].get(_count_url(payments_count_context))
    assert response.status_code == expected_status


def test_household_payments_count_empty(
    create_user_role_with_permissions: Any,
    payments_count_context: dict[str, Any],
) -> None:
    create_user_role_with_permissions(
        user=payments_count_context["user"],
        permissions=[Permissions.POPULATION_VIEW_HOUSEHOLDS_DETAILS],
        business_area=payments_count_context["afghanistan"],
        program=payments_count_context["program"],
    )
    response = payments_count_context["api_client"].get(_count_url(payments_count_context))
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"count": 0}


def test_household_payments_count_includes_only_eligible_and_non_pre_status(
    create_user_role_with_permissions: Any,
    payments_count_context: dict[str, Any],
) -> None:
    create_user_role_with_permissions(
        user=payments_count_context["user"],
        permissions=[Permissions.POPULATION_VIEW_HOUSEHOLDS_DETAILS],
        business_area=payments_count_context["afghanistan"],
        program=payments_count_context["program"],
    )

    # Eligible payments attached to plans past the pre-plan stage — SHOULD count.
    _make_payment(payments_count_context, PaymentPlan.Status.OPEN)
    _make_payment(payments_count_context, PaymentPlan.Status.LOCKED)
    _make_payment(payments_count_context, PaymentPlan.Status.ACCEPTED)

    # Parent plan still in a pre-payment-plan status — SHOULD NOT count.
    _make_payment(payments_count_context, PaymentPlan.Status.TP_OPEN)
    _make_payment(payments_count_context, PaymentPlan.Status.TP_LOCKED)
    _make_payment(payments_count_context, PaymentPlan.Status.DRAFT)

    # Non-eligible payments on a valid-status plan — SHOULD NOT count.
    _make_payment(payments_count_context, PaymentPlan.Status.OPEN, conflicted=True)
    _make_payment(payments_count_context, PaymentPlan.Status.OPEN, excluded=True)
    _make_payment(payments_count_context, PaymentPlan.Status.OPEN, has_valid_wallet=False)

    # Payment belonging to a different household — SHOULD NOT count.
    other_household = HouseholdFactory(
        program=payments_count_context["program"],
        business_area=payments_count_context["afghanistan"],
    )
    other_plan = PaymentPlanFactory(
        status=PaymentPlan.Status.OPEN,
        program_cycle__program=payments_count_context["program"],
        business_area=payments_count_context["afghanistan"],
    )
    PaymentFactory(
        parent=other_plan,
        household=other_household,
        business_area=payments_count_context["afghanistan"],
        currency=other_household.currency,
    )

    response = payments_count_context["api_client"].get(_count_url(payments_count_context))

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"count": 3}
