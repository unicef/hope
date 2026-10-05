"""A no-op round-trip must not repoint a Payment Plan Group onto the active currency row.

Echoing back the code a ``GET`` handed out must leave the group on the row it was on.
"""

from typing import Any, Callable

import pytest
from rest_framework import status
from rest_framework.reverse import reverse

from extras.test_utils.factories import (
    BusinessAreaFactory,
    CurrencyFactory,
    PaymentPlanGroupFactory,
    ProgramCycleFactory,
    ProgramFactory,
    UserFactory,
)
from hope.apps.account.permissions import Permissions
from hope.models import Currency, PaymentPlanGroup, Program

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
def round_trip_context(
    api_client: Callable,
    create_user_role_with_permissions: Any,
    deprecated_syp: Currency,
    active_syp: Currency,
) -> dict[str, Any]:
    business_area = BusinessAreaFactory(slug="afghanistan")
    program = ProgramFactory(business_area=business_area, status=Program.ACTIVE)
    cycle = ProgramCycleFactory(program=program)
    user = UserFactory()
    create_user_role_with_permissions(user, [Permissions.PM_PAYMENT_PLAN_GROUP_UPDATE], business_area, program)
    payment_plan_group = PaymentPlanGroupFactory(name="Old SYP group", cycle=cycle, currency=deprecated_syp)
    url = reverse(
        "api:payments:payment-plan-groups-detail",
        kwargs={
            "business_area_slug": business_area.slug,
            "program_code": program.code,
            "pk": payment_plan_group.pk,
        },
    )
    return {
        "payment_plan_group": payment_plan_group,
        "client": api_client(user),
        "url": url,
    }


@pytest.fixture
def create_context(api_client: Callable, create_user_role_with_permissions: Any) -> dict[str, Any]:
    business_area = BusinessAreaFactory(slug="afghanistan")
    program = ProgramFactory(business_area=business_area, status=Program.ACTIVE)
    cycle = ProgramCycleFactory(program=program)
    user = UserFactory()
    create_user_role_with_permissions(user, [Permissions.PM_PAYMENT_PLAN_GROUP_CREATE], business_area, program)
    url = reverse(
        "api:payments:payment-plan-groups-list",
        kwargs={"business_area_slug": business_area.slug, "program_code": program.code},
    )
    return {"cycle": cycle, "client": api_client(user), "url": url}


def test_update_arrange_group_on_deprecated_currency_act_put_same_code_assert_currency_unchanged(
    round_trip_context: dict[str, Any],
    deprecated_syp: Currency,
) -> None:
    payment_plan_group = round_trip_context["payment_plan_group"]

    response = round_trip_context["client"].put(
        round_trip_context["url"],
        {"name": "Renamed SYP group", "currency": "SYP"},
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK
    payment_plan_group.refresh_from_db()
    assert payment_plan_group.currency_id == deprecated_syp.pk
    assert payment_plan_group.name == "Renamed SYP group"


def test_update_arrange_group_on_deprecated_currency_act_put_other_code_assert_resolves_to_active(
    round_trip_context: dict[str, Any],
    currency_eur: Currency,
) -> None:
    payment_plan_group = round_trip_context["payment_plan_group"]

    response = round_trip_context["client"].put(
        round_trip_context["url"],
        {"name": payment_plan_group.name, "currency": "EUR"},
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK
    payment_plan_group.refresh_from_db()
    assert payment_plan_group.currency_id == currency_eur.pk


def test_update_arrange_group_on_active_currency_act_put_same_code_assert_stays_on_active(
    round_trip_context: dict[str, Any],
    active_syp: Currency,
) -> None:
    payment_plan_group = round_trip_context["payment_plan_group"]
    payment_plan_group.currency = active_syp
    payment_plan_group.save(update_fields=["currency"])

    response = round_trip_context["client"].put(
        round_trip_context["url"],
        {"name": payment_plan_group.name, "currency": "SYP"},
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK
    payment_plan_group.refresh_from_db()
    assert payment_plan_group.currency_id == active_syp.pk


def test_create_arrange_two_syp_rows_act_post_code_assert_group_on_active_row(
    create_context: dict[str, Any],
    deprecated_syp: Currency,
    active_syp: Currency,
) -> None:
    response = create_context["client"].post(
        create_context["url"],
        {"name": "New SYP group", "cycle": str(create_context["cycle"].id), "currency": "SYP"},
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert PaymentPlanGroup.objects.get(id=response.json()["id"]).currency_id == active_syp.pk
