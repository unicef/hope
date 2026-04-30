from decimal import Decimal
from typing import Any, Callable

from django.urls import reverse
import pytest
from rest_framework import status

from extras.test_utils.factories import (
    BusinessAreaFactory,
    PaymentPlanFactory,
    PaymentPlanGroupFactory,
    ProgramCycleFactory,
    ProgramFactory,
    UserFactory,
)
from hope.apps.account.permissions import Permissions
from hope.models import PaymentPlanGroup

pytestmark = pytest.mark.django_db


@pytest.fixture
def business_area() -> Any:
    return BusinessAreaFactory(slug="test-ba")


@pytest.fixture
def program(business_area: Any) -> Any:
    return ProgramFactory(business_area=business_area)


@pytest.fixture
def cycle(program: Any) -> Any:
    return ProgramCycleFactory(program=program)


@pytest.fixture
def user() -> Any:
    return UserFactory()


def _list_url(ba_slug: str) -> str:
    return reverse("api:payments:payment-plan-groups-list", kwargs={"business_area_slug": ba_slug})


def _detail_url(ba_slug: str, group_id: Any) -> str:
    return reverse("api:payments:payment-plan-groups-detail", kwargs={"business_area_slug": ba_slug, "pk": group_id})


def test_list_groups_for_cycle(
    api_client: Callable,
    user: Any,
    business_area: Any,
    cycle: Any,
    create_user_role_with_permissions: Any,
) -> None:
    client = api_client(user)
    create_user_role_with_permissions(user, [Permissions.PM_VIEW_PAYMENT_PLAN_GROUP], business_area)

    ProgramCycleFactory(program=cycle.program)

    response = client.get(_list_url(business_area.slug), {"cycle": str(cycle.id)})

    assert response.status_code == status.HTTP_200_OK
    results = response.json()["results"]
    assert len(results) == 1
    assert results[0]["cycle"] == str(cycle.id)


def test_list_groups_no_cycle_filter(
    api_client: Callable,
    user: Any,
    business_area: Any,
    cycle: Any,
    create_user_role_with_permissions: Any,
) -> None:
    client = api_client(user)
    create_user_role_with_permissions(user, [Permissions.PM_VIEW_PAYMENT_PLAN_GROUP], business_area)

    # cycle auto-creates 1 group; second cycle auto-creates another
    ProgramCycleFactory(program=cycle.program)

    response = client.get(_list_url(business_area.slug))

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["results"]) == 2


def test_create_group_under_cycle(
    api_client: Callable,
    user: Any,
    business_area: Any,
    cycle: Any,
    create_user_role_with_permissions: Any,
) -> None:
    client = api_client(user)
    create_user_role_with_permissions(user, [Permissions.PM_CREATE_PAYMENT_PLAN_GROUP], business_area)

    response = client.post(_list_url(business_area.slug), {"name": "New Group", "cycle": str(cycle.id)})

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == "New Group"
    assert data["cycle"] == str(cycle.id)
    assert data["unicef_id"] is not None
    assert PaymentPlanGroup.objects.filter(id=data["id"]).exists()


def test_retrieve_detail_aggregated_totals(
    api_client: Callable,
    user: Any,
    business_area: Any,
    cycle: Any,
    create_user_role_with_permissions: Any,
) -> None:
    client = api_client(user)
    create_user_role_with_permissions(user, [Permissions.PM_VIEW_PAYMENT_PLAN_GROUP], business_area)

    group = cycle.payment_plan_groups.get()
    PaymentPlanFactory(
        business_area=business_area,
        program_cycle=cycle,
        payment_plan_group=group,
        total_entitled_quantity_usd=Decimal("100.00"),
        total_delivered_quantity_usd=Decimal("60.00"),
        total_undelivered_quantity_usd=Decimal("40.00"),
    )
    PaymentPlanFactory(
        business_area=business_area,
        program_cycle=cycle,
        payment_plan_group=group,
        total_entitled_quantity_usd=Decimal("200.00"),
        total_delivered_quantity_usd=Decimal("150.00"),
        total_undelivered_quantity_usd=Decimal("50.00"),
    )

    response = client.get(_detail_url(business_area.slug, group.id))

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert Decimal(data["total_entitled_quantity_usd"]) == Decimal("300.00")
    assert Decimal(data["total_delivered_quantity_usd"]) == Decimal("210.00")
    assert Decimal(data["total_undelivered_quantity_usd"]) == Decimal("90.00")
    assert data["payment_plans_count"] == 2


def test_delete_group_with_no_plans_succeeds(
    api_client: Callable,
    user: Any,
    business_area: Any,
    cycle: Any,
    create_user_role_with_permissions: Any,
) -> None:
    client = api_client(user)
    create_user_role_with_permissions(user, [Permissions.PM_DELETE_PAYMENT_PLAN_GROUP], business_area)

    # create a second group to delete (the default group is kept)
    group = PaymentPlanGroupFactory(cycle=cycle)

    response = client.delete(_detail_url(business_area.slug, group.id))

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not PaymentPlanGroup.objects.filter(id=group.id).exists()


def test_delete_group_with_plans_blocked(
    api_client: Callable,
    user: Any,
    business_area: Any,
    cycle: Any,
    create_user_role_with_permissions: Any,
) -> None:
    client = api_client(user)
    create_user_role_with_permissions(user, [Permissions.PM_DELETE_PAYMENT_PLAN_GROUP], business_area)

    group = cycle.payment_plan_groups.get()
    PaymentPlanFactory(business_area=business_area, program_cycle=cycle, payment_plan_group=group)

    response = client.delete(_detail_url(business_area.slug, group.id))

    assert response.status_code == status.HTTP_409_CONFLICT
    assert PaymentPlanGroup.objects.filter(id=group.id).exists()


def test_list_excludes_other_business_area(
    api_client: Callable,
    user: Any,
    business_area: Any,
    cycle: Any,
    create_user_role_with_permissions: Any,
) -> None:
    client = api_client(user)
    create_user_role_with_permissions(user, [Permissions.PM_VIEW_PAYMENT_PLAN_GROUP], business_area)

    # cycle auto-creates 1 group in business_area
    other_ba = BusinessAreaFactory(slug="other-ba")
    other_program = ProgramFactory(business_area=other_ba)
    ProgramCycleFactory(program=other_program)  # auto-creates 1 group in other_ba

    response = client.get(_list_url(business_area.slug))

    assert response.status_code == status.HTTP_200_OK
    results = response.json()["results"]
    assert len(results) == 1
    assert results[0]["cycle"] == str(cycle.id)


def test_list_permission_denied(
    api_client: Callable,
    user: Any,
    business_area: Any,
    create_user_role_with_permissions: Any,
) -> None:
    client = api_client(user)
    create_user_role_with_permissions(user, [], business_area)

    response = client.get(_list_url(business_area.slug))

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_create_permission_denied(
    api_client: Callable,
    user: Any,
    business_area: Any,
    cycle: Any,
    create_user_role_with_permissions: Any,
) -> None:
    client = api_client(user)
    create_user_role_with_permissions(user, [], business_area)

    response = client.post(_list_url(business_area.slug), {"name": "X", "cycle": str(cycle.id)})

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_delete_permission_denied(
    api_client: Callable,
    user: Any,
    business_area: Any,
    cycle: Any,
    create_user_role_with_permissions: Any,
) -> None:
    client = api_client(user)
    create_user_role_with_permissions(user, [], business_area)

    group = cycle.payment_plan_groups.get()

    response = client.delete(_detail_url(business_area.slug, group.id))

    assert response.status_code == status.HTTP_403_FORBIDDEN
