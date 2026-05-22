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
from hope.models import Payment, PaymentPlan, Program

pytestmark = pytest.mark.django_db


@pytest.fixture
def business_area() -> Any:
    return BusinessAreaFactory(slug="afghanistan")


@pytest.fixture
def amendment_view_context(api_client: Callable, business_area: Any) -> dict[str, Any]:
    user = UserFactory()
    program = ProgramFactory(business_area=business_area, status=Program.ACTIVE)
    cycle = ProgramCycleFactory(program=program)
    currency = CurrencyFactory(code="PLN", name="Polish Zloty")
    regular_pp = PaymentPlanFactory(
        business_area=business_area,
        program_cycle=cycle,
        plan_type=PaymentPlan.PlanType.REGULAR,
        currency=currency,
    )
    top_up_pp = PaymentPlanFactory(
        name="Standard PP Top Up",
        business_area=business_area,
        program_cycle=cycle,
        plan_type=PaymentPlan.PlanType.TOP_UP,
        source_payment_plan=regular_pp,
        currency=currency,
    )
    purpose = PaymentPlanPurposeFactory(business_area=business_area)
    top_up_pp.payment_plan_purposes.add(purpose)
    PaymentFactory(parent=top_up_pp, status=Payment.STATUS_DISTRIBUTION_SUCCESS)
    url = reverse(
        "api:payments:payment-plans-create-top-up-amendment",
        kwargs={
            "business_area_slug": business_area.slug,
            "program_code": program.code,
            "pk": top_up_pp.pk,
        },
    )
    return {
        "business_area": business_area,
        "user": user,
        "program": program,
        "top_up_pp": top_up_pp,
        "client": api_client(user),
        "url": url,
    }


@pytest.mark.parametrize(
    ("permissions", "expected_status"),
    [
        ([Permissions.PM_CREATE], status.HTTP_201_CREATED),
        ([], status.HTTP_403_FORBIDDEN),
    ],
)
def test_create_top_up_amendment_view_arrange_permissions_act_post_assert_status(
    amendment_view_context: dict[str, Any],
    create_user_role_with_permissions: Any,
    permissions: list,
    expected_status: int,
) -> None:
    create_user_role_with_permissions(
        amendment_view_context["user"],
        permissions,
        amendment_view_context["business_area"],
        amendment_view_context["program"],
    )

    response = amendment_view_context["client"].post(
        amendment_view_context["url"],
        {"dispersion_start_date": "2024-01-01", "dispersion_end_date": "2026-01-01"},
        format="json",
    )

    assert response.status_code == expected_status


def test_create_top_up_amendment_view_arrange_eligible_top_up_act_post_assert_amendment_payload(
    amendment_view_context: dict[str, Any],
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        amendment_view_context["user"],
        [Permissions.PM_CREATE],
        amendment_view_context["business_area"],
        amendment_view_context["program"],
    )

    response = amendment_view_context["client"].post(
        amendment_view_context["url"],
        {"dispersion_start_date": "2024-01-01", "dispersion_end_date": "2026-01-01"},
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["plan_type"] == PaymentPlan.PlanType.TOP_UP_AMENDMENT
    assert data["name"] == "Standard PP Top Up Amendment"
    assert "id" in data["source_payment_plan"]


def test_create_top_up_amendment_view_arrange_missing_dispersion_dates_act_post_assert_400(
    amendment_view_context: dict[str, Any],
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        amendment_view_context["user"],
        [Permissions.PM_CREATE],
        amendment_view_context["business_area"],
        amendment_view_context["program"],
    )

    response = amendment_view_context["client"].post(amendment_view_context["url"], {}, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
