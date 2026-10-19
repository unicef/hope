"""A no-op round-trip must not repoint a plan onto the active currency row.

Echoing back the code a ``GET`` handed out must leave the plan and its payments where they were.
Covers both the ``PATCH`` and the ``POST`` that opens a target population -- the latter reads as
a create but overwrites an existing plan's currency.
"""

from typing import Any, Callable

import pytest
from rest_framework import status
from rest_framework.reverse import reverse

from extras.test_utils.factories import (
    BusinessAreaFactory,
    CurrencyFactory,
    PaymentFactory,
    PaymentPlanFactory,
    ProgramCycleFactory,
    ProgramFactory,
    UserFactory,
)
from hope.apps.account.permissions import Permissions
from hope.models import Currency, PaymentPlan, Program

pytestmark = pytest.mark.django_db


@pytest.fixture
def deprecated_syp() -> Currency:
    return CurrencyFactory(code="SYP", vision_code="SYP", name="Syrian pound Old", active=False)


@pytest.fixture
def active_syp() -> Currency:
    return CurrencyFactory(code="SYP", vision_code="SYP01", name="Syrian pound", active=True)


@pytest.fixture
def currency_eur() -> Currency:
    return CurrencyFactory(code="EUR", vision_code="EUR", name="Euro")


@pytest.fixture
def round_trip_context(api_client: Callable, deprecated_syp: Currency, active_syp: Currency) -> dict[str, Any]:
    business_area = BusinessAreaFactory(slug="afghanistan")
    program = ProgramFactory(business_area=business_area, status=Program.ACTIVE)
    cycle = ProgramCycleFactory(program=program)
    user = UserFactory()
    payment_plan = PaymentPlanFactory(
        name="Old SYP plan",
        business_area=business_area,
        program_cycle=cycle,
        plan_type=PaymentPlan.PlanType.REGULAR,
        status=PaymentPlan.Status.ACCEPTED,
        currency=deprecated_syp,
    )
    payments = [PaymentFactory(parent=payment_plan, currency=deprecated_syp) for _ in range(2)]
    url = reverse(
        "api:payments:payment-plans-detail",
        kwargs={
            "business_area_slug": business_area.slug,
            "program_code": program.code,
            "pk": payment_plan.pk,
        },
    )
    return {
        "business_area": business_area,
        "program": program,
        "user": user,
        "payment_plan": payment_plan,
        "payments": payments,
        "client": api_client(user),
        "url": url,
    }


def test_partial_update_arrange_plan_on_deprecated_currency_act_patch_dates_assert_currency_unchanged(
    round_trip_context: dict[str, Any],
    create_user_role_with_permissions: Any,
    deprecated_syp: Currency,
) -> None:
    create_user_role_with_permissions(
        round_trip_context["user"],
        [Permissions.PM_CREATE, Permissions.PM_VIEW_DETAILS],
        round_trip_context["business_area"],
        round_trip_context["program"],
    )
    payment_plan = round_trip_context["payment_plan"]

    response = round_trip_context["client"].patch(
        round_trip_context["url"],
        {
            "dispersion_start_date": "2024-01-01",
            "dispersion_end_date": "2099-12-31",
            "currency": "SYP",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK
    payment_plan.refresh_from_db()
    assert payment_plan.currency_id == deprecated_syp.pk
    assert str(payment_plan.dispersion_end_date) == "2099-12-31"
    assert list(payment_plan.payment_items.values_list("currency_id", flat=True)) == [
        deprecated_syp.pk,
        deprecated_syp.pk,
    ]


def test_partial_update_arrange_plan_on_deprecated_currency_act_patch_other_code_assert_resolves_to_active(
    round_trip_context: dict[str, Any],
    create_user_role_with_permissions: Any,
    currency_eur: Currency,
) -> None:
    create_user_role_with_permissions(
        round_trip_context["user"],
        [Permissions.PM_CREATE, Permissions.PM_VIEW_DETAILS],
        round_trip_context["business_area"],
        round_trip_context["program"],
    )
    payment_plan = round_trip_context["payment_plan"]

    response = round_trip_context["client"].patch(
        round_trip_context["url"],
        {"currency": "EUR"},
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK
    payment_plan.refresh_from_db()
    assert payment_plan.currency_id == currency_eur.pk


def test_partial_update_arrange_plan_on_active_currency_act_patch_same_code_assert_stays_on_active(
    round_trip_context: dict[str, Any],
    create_user_role_with_permissions: Any,
    active_syp: Currency,
) -> None:
    create_user_role_with_permissions(
        round_trip_context["user"],
        [Permissions.PM_CREATE, Permissions.PM_VIEW_DETAILS],
        round_trip_context["business_area"],
        round_trip_context["program"],
    )
    payment_plan = round_trip_context["payment_plan"]
    payment_plan.currency = active_syp
    payment_plan.save(update_fields=["currency"])

    response = round_trip_context["client"].patch(
        round_trip_context["url"],
        {"currency": "SYP"},
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK
    payment_plan.refresh_from_db()
    assert payment_plan.currency_id == active_syp.pk


@pytest.fixture
def open_context(api_client: Callable, deprecated_syp: Currency, active_syp: Currency) -> dict[str, Any]:
    business_area = BusinessAreaFactory(slug="afghanistan")
    program = ProgramFactory(business_area=business_area, status=Program.ACTIVE)
    cycle = program.cycles.first()
    user = UserFactory()
    payment_plan = PaymentPlanFactory(
        name="Target population on old SYP",
        business_area=business_area,
        program_cycle=cycle,
        status=PaymentPlan.Status.DRAFT,
        currency=deprecated_syp,
    )
    payments = [PaymentFactory(parent=payment_plan, currency=deprecated_syp) for _ in range(2)]
    url = reverse(
        "api:payments:payment-plans-list",
        kwargs={"business_area_slug": business_area.slug, "program_code": program.code},
    )
    return {
        "business_area": business_area,
        "program": program,
        "user": user,
        "payment_plan": payment_plan,
        "payments": payments,
        "client": api_client(user),
        "url": url,
    }


def test_open_arrange_target_population_on_deprecated_currency_act_post_same_code_assert_currency_unchanged(
    open_context: dict[str, Any],
    create_user_role_with_permissions: Any,
    deprecated_syp: Currency,
) -> None:
    create_user_role_with_permissions(
        open_context["user"],
        [Permissions.PM_CREATE, Permissions.PM_VIEW_DETAILS],
        open_context["business_area"],
        open_context["program"],
    )
    payment_plan = open_context["payment_plan"]

    response = open_context["client"].post(
        open_context["url"],
        {
            "target_population_id": str(payment_plan.pk),
            "dispersion_start_date": "2024-01-01",
            "dispersion_end_date": "2099-12-31",
            "currency": "SYP",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED
    payment_plan.refresh_from_db()
    assert payment_plan.currency_id == deprecated_syp.pk
    assert list(payment_plan.payment_items.values_list("currency_id", flat=True)) == [
        deprecated_syp.pk,
        deprecated_syp.pk,
    ]


def test_open_arrange_target_population_on_deprecated_currency_act_post_other_code_assert_resolves_to_active(
    open_context: dict[str, Any],
    create_user_role_with_permissions: Any,
    currency_eur: Currency,
) -> None:
    create_user_role_with_permissions(
        open_context["user"],
        [Permissions.PM_CREATE, Permissions.PM_VIEW_DETAILS],
        open_context["business_area"],
        open_context["program"],
    )
    payment_plan = open_context["payment_plan"]

    response = open_context["client"].post(
        open_context["url"],
        {
            "target_population_id": str(payment_plan.pk),
            "dispersion_start_date": "2024-01-01",
            "dispersion_end_date": "2099-12-31",
            "currency": "EUR",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED
    payment_plan.refresh_from_db()
    assert payment_plan.currency_id == currency_eur.pk
    assert list(payment_plan.payment_items.values_list("currency_id", flat=True)) == [
        currency_eur.pk,
        currency_eur.pk,
    ]
