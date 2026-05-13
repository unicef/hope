from decimal import Decimal
from typing import Any, Callable

from django.db import connection
from django.test import TestCase
from django.test.utils import CaptureQueriesContext
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


@pytest.fixture
def client(api_client: Callable, user: Any) -> Any:
    return api_client(user)


def _list_url(ba_slug: str, program_code: str) -> str:
    return reverse(
        "api:payments:payment-plan-groups-list",
        kwargs={"business_area_slug": ba_slug, "program_code": program_code},
    )


def _count_url(ba_slug: str, program_code: str) -> str:
    return reverse(
        "api:payments:payment-plan-groups-count",
        kwargs={"business_area_slug": ba_slug, "program_code": program_code},
    )


def _detail_url(ba_slug: str, program_code: str, group_id: Any) -> str:
    return reverse(
        "api:payments:payment-plan-groups-detail",
        kwargs={"business_area_slug": ba_slug, "program_code": program_code, "pk": group_id},
    )


def test_list_groups_for_cycle(
    client: Any,
    user: Any,
    business_area: Any,
    program: Any,
    cycle: Any,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        user, [Permissions.PM_PAYMENT_PLAN_GROUP_VIEW_LIST], business_area, program=program
    )

    ProgramCycleFactory(program=cycle.program)

    with CaptureQueriesContext(connection) as ctx:
        response = client.get(_list_url(business_area.slug, program.code), {"cycle": str(cycle.id)})

    assert response.status_code == status.HTTP_200_OK
    results = response.json()["results"]
    assert len(results) == 1
    assert results[0]["cycle"] == {"id": str(cycle.id), "title": cycle.title}
    assert len(ctx.captured_queries) == 13


def test_list_groups_no_cycle_filter(
    client: Any,
    user: Any,
    business_area: Any,
    program: Any,
    cycle: Any,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        user, [Permissions.PM_PAYMENT_PLAN_GROUP_VIEW_LIST], business_area, program=program
    )

    # cycle auto-creates 1 group; second cycle auto-creates another
    ProgramCycleFactory(program=cycle.program)

    with CaptureQueriesContext(connection) as ctx:
        response = client.get(_list_url(business_area.slug, program.code))

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["results"]) == 2
    assert len(ctx.captured_queries) == 13


def test_count_groups_for_cycle(
    client: Any,
    user: Any,
    business_area: Any,
    program: Any,
    cycle: Any,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        user, [Permissions.PM_PAYMENT_PLAN_GROUP_VIEW_LIST], business_area, program=program
    )
    ProgramCycleFactory(program=cycle.program)  # group from this cycle should not be included
    PaymentPlanGroupFactory(cycle=cycle)

    response = client.get(_count_url(business_area.slug, program.code), {"cycle": str(cycle.id)})

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["count"] == 2  # default group + one added


def test_count_groups_no_cycle_filter(
    client: Any,
    user: Any,
    business_area: Any,
    program: Any,
    cycle: Any,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        user, [Permissions.PM_PAYMENT_PLAN_GROUP_VIEW_LIST], business_area, program=program
    )
    ProgramCycleFactory(program=cycle.program)

    response = client.get(_count_url(business_area.slug, program.code))

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["count"] == 2  # one default group per cycle


def test_create_group_under_cycle(
    client: Any,
    user: Any,
    business_area: Any,
    program: Any,
    cycle: Any,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(user, [Permissions.PM_PAYMENT_PLAN_GROUP_CREATE], business_area, program=program)

    response = client.post(_list_url(business_area.slug, program.code), {"name": "New Group", "cycle": str(cycle.id)})

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == "New Group"
    assert data["cycle"] == str(cycle.id)
    assert data["unicef_id"] is not None
    assert PaymentPlanGroup.objects.filter(id=data["id"]).exists()


def test_create_group_duplicate_name_in_same_cycle_rejected(
    client: Any,
    user: Any,
    business_area: Any,
    program: Any,
    cycle: Any,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(user, [Permissions.PM_PAYMENT_PLAN_GROUP_CREATE], business_area, program=program)

    PaymentPlanGroupFactory(cycle=cycle, name="Existing Group")

    response = client.post(
        _list_url(business_area.slug, program.code), {"name": "Existing Group", "cycle": str(cycle.id)}
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["name"][0] == "A group named 'Existing Group' already exists in this cycle."


def test_create_group_same_name_different_cycle_allowed(
    client: Any,
    user: Any,
    business_area: Any,
    program: Any,
    cycle: Any,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(user, [Permissions.PM_PAYMENT_PLAN_GROUP_CREATE], business_area, program=program)

    other_cycle = ProgramCycleFactory(program=program)
    PaymentPlanGroupFactory(cycle=other_cycle, name="Shared Name")

    response = client.post(_list_url(business_area.slug, program.code), {"name": "Shared Name", "cycle": str(cycle.id)})

    assert response.status_code == status.HTTP_201_CREATED


def test_retrieve_detail_aggregated_totals(
    client: Any,
    user: Any,
    business_area: Any,
    program: Any,
    cycle: Any,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        user, [Permissions.PM_PAYMENT_PLAN_GROUP_VIEW_DETAIL], business_area, program=program
    )

    group = cycle.payment_plan_groups.first()
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

    response = client.get(_detail_url(business_area.slug, program.code, group.id))

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert Decimal(data["total_entitled_quantity_usd"]) == Decimal("300.00")
    assert Decimal(data["total_delivered_quantity_usd"]) == Decimal("210.00")
    assert Decimal(data["total_undelivered_quantity_usd"]) == Decimal("90.00")
    assert data["payment_plans_count"] == 2


def test_delete_group_with_no_plans_succeeds(
    client: Any,
    user: Any,
    business_area: Any,
    program: Any,
    cycle: Any,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(user, [Permissions.PM_PAYMENT_PLAN_GROUP_DELETE], business_area, program=program)

    # create a second group to delete (the default group is kept)
    group = PaymentPlanGroupFactory(cycle=cycle)

    response = client.delete(_detail_url(business_area.slug, program.code, group.id))

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not PaymentPlanGroup.objects.filter(id=group.id).exists()


def test_delete_last_group_in_cycle_blocked(
    client: Any,
    user: Any,
    business_area: Any,
    program: Any,
    cycle: Any,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(user, [Permissions.PM_PAYMENT_PLAN_GROUP_DELETE], business_area, program=program)

    group = cycle.payment_plan_groups.get()

    response = client.delete(_detail_url(business_area.slug, program.code, group.id))

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()[0] == "Cannot delete the last group in a cycle."
    assert PaymentPlanGroup.objects.filter(id=group.id).exists()


def test_delete_group_with_plans_blocked(
    client: Any,
    user: Any,
    business_area: Any,
    program: Any,
    cycle: Any,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(user, [Permissions.PM_PAYMENT_PLAN_GROUP_DELETE], business_area, program=program)

    group = cycle.payment_plan_groups.first()
    PaymentPlanFactory(business_area=business_area, program_cycle=cycle, payment_plan_group=group)

    response = client.delete(_detail_url(business_area.slug, program.code, group.id))

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()[0] == "Cannot delete a group that has payment plans."
    assert PaymentPlanGroup.objects.filter(id=group.id).exists()


def test_list_excludes_other_business_area(
    client: Any,
    user: Any,
    business_area: Any,
    program: Any,
    cycle: Any,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        user, [Permissions.PM_PAYMENT_PLAN_GROUP_VIEW_LIST], business_area, program=program
    )

    # cycle auto-creates 1 group in business_area
    other_ba = BusinessAreaFactory(slug="other-ba")
    other_program = ProgramFactory(business_area=other_ba)
    ProgramCycleFactory(program=other_program)  # auto-creates 1 group in other_ba

    response = client.get(_list_url(business_area.slug, program.code))

    assert response.status_code == status.HTTP_200_OK
    results = response.json()["results"]
    assert len(results) == 1
    assert results[0]["cycle"]["id"] == str(cycle.id)


@pytest.mark.parametrize(
    ("permissions", "expected_status"),
    [
        ([Permissions.PM_PAYMENT_PLAN_GROUP_VIEW_LIST], status.HTTP_200_OK),
        ([Permissions.PM_PAYMENT_PLAN_GROUP_CREATE], status.HTTP_403_FORBIDDEN),
        ([], status.HTTP_403_FORBIDDEN),
    ],
)
def test_list_permissions(
    client: Any,
    user: Any,
    business_area: Any,
    program: Any,
    create_user_role_with_permissions: Any,
    permissions: list,
    expected_status: int,
) -> None:
    create_user_role_with_permissions(user, permissions, business_area, program=program)

    response = client.get(_list_url(business_area.slug, program.code))

    assert response.status_code == expected_status


@pytest.mark.parametrize(
    ("permissions", "expected_status"),
    [
        ([Permissions.PM_PAYMENT_PLAN_GROUP_CREATE], status.HTTP_201_CREATED),
        ([Permissions.PM_PAYMENT_PLAN_GROUP_VIEW_LIST], status.HTTP_403_FORBIDDEN),
        ([], status.HTTP_403_FORBIDDEN),
    ],
)
def test_create_permissions(
    client: Any,
    user: Any,
    business_area: Any,
    program: Any,
    cycle: Any,
    create_user_role_with_permissions: Any,
    permissions: list,
    expected_status: int,
) -> None:
    create_user_role_with_permissions(user, permissions, business_area, program=program)

    response = client.post(_list_url(business_area.slug, program.code), {"name": "X", "cycle": str(cycle.id)})

    assert response.status_code == expected_status


@pytest.mark.parametrize(
    ("permissions", "expected_status"),
    [
        ([Permissions.PM_PAYMENT_PLAN_GROUP_VIEW_DETAIL], status.HTTP_200_OK),
        ([Permissions.PM_PAYMENT_PLAN_GROUP_VIEW_LIST], status.HTTP_403_FORBIDDEN),
        ([], status.HTTP_403_FORBIDDEN),
    ],
)
def test_retrieve_permissions(
    client: Any,
    user: Any,
    business_area: Any,
    program: Any,
    cycle: Any,
    create_user_role_with_permissions: Any,
    permissions: list,
    expected_status: int,
) -> None:
    create_user_role_with_permissions(user, permissions, business_area, program=program)

    group = cycle.payment_plan_groups.first()

    response = client.get(_detail_url(business_area.slug, program.code, group.id))

    assert response.status_code == expected_status


@pytest.mark.parametrize(
    ("permissions", "expected_status"),
    [
        ([Permissions.PM_PAYMENT_PLAN_GROUP_UPDATE], status.HTTP_200_OK),
        ([Permissions.PM_PAYMENT_PLAN_GROUP_VIEW_LIST], status.HTTP_403_FORBIDDEN),
        ([], status.HTTP_403_FORBIDDEN),
    ],
)
def test_update_permissions(
    client: Any,
    user: Any,
    business_area: Any,
    program: Any,
    cycle: Any,
    create_user_role_with_permissions: Any,
    permissions: list,
    expected_status: int,
) -> None:
    create_user_role_with_permissions(user, permissions, business_area, program=program)

    group = cycle.payment_plan_groups.first()

    response = client.put(_detail_url(business_area.slug, program.code, group.id), {"name": "Renamed"})

    assert response.status_code == expected_status


@pytest.mark.parametrize(
    ("permissions", "expected_status"),
    [
        ([Permissions.PM_PAYMENT_PLAN_GROUP_DELETE], status.HTTP_204_NO_CONTENT),
        ([Permissions.PM_PAYMENT_PLAN_GROUP_VIEW_LIST], status.HTTP_403_FORBIDDEN),
        ([], status.HTTP_403_FORBIDDEN),
    ],
)
def test_delete_permissions(
    client: Any,
    user: Any,
    business_area: Any,
    program: Any,
    cycle: Any,
    create_user_role_with_permissions: Any,
    permissions: list,
    expected_status: int,
) -> None:
    create_user_role_with_permissions(user, permissions, business_area, program=program)

    group = PaymentPlanGroupFactory(cycle=cycle)

    response = client.delete(_detail_url(business_area.slug, program.code, group.id))

    assert response.status_code == expected_status


def test_update_group_name_succeeds(
    client: Any,
    user: Any,
    business_area: Any,
    program: Any,
    cycle: Any,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(user, [Permissions.PM_PAYMENT_PLAN_GROUP_UPDATE], business_area, program=program)

    group = cycle.payment_plan_groups.first()

    response = client.put(_detail_url(business_area.slug, program.code, group.id), {"name": "Renamed Group"})

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["name"] == "Renamed Group"
    group.refresh_from_db()
    assert group.name == "Renamed Group"


def test_update_group_name_duplicate_in_same_cycle_rejected(
    client: Any,
    user: Any,
    business_area: Any,
    program: Any,
    cycle: Any,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(user, [Permissions.PM_PAYMENT_PLAN_GROUP_UPDATE], business_area, program=program)

    other_group = PaymentPlanGroupFactory(cycle=cycle, name="Taken Name")
    group = cycle.payment_plan_groups.exclude(pk=other_group.pk).first()

    response = client.put(_detail_url(business_area.slug, program.code, group.id), {"name": "Taken Name"})

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Taken Name" in response.json()["name"][0]


def test_update_group_name_same_as_self_succeeds(
    client: Any,
    user: Any,
    business_area: Any,
    program: Any,
    cycle: Any,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(user, [Permissions.PM_PAYMENT_PLAN_GROUP_UPDATE], business_area, program=program)

    group = cycle.payment_plan_groups.first()
    original_name = group.name

    response = client.put(_detail_url(business_area.slug, program.code, group.id), {"name": original_name})

    assert response.status_code == status.HTTP_200_OK


def test_update_group_name_same_as_other_cycle_allowed(
    client: Any,
    user: Any,
    business_area: Any,
    program: Any,
    cycle: Any,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(user, [Permissions.PM_PAYMENT_PLAN_GROUP_UPDATE], business_area, program=program)

    other_cycle = ProgramCycleFactory(program=program)
    PaymentPlanGroupFactory(cycle=other_cycle, name="Shared Name")
    group = cycle.payment_plan_groups.first()

    response = client.put(_detail_url(business_area.slug, program.code, group.id), {"name": "Shared Name"})

    assert response.status_code == status.HTTP_200_OK


def test_list_cache_invalidated_on_group_create(
    client: Any,
    user: Any,
    business_area: Any,
    program: Any,
    cycle: Any,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PM_PAYMENT_PLAN_GROUP_VIEW_LIST, Permissions.PM_PAYMENT_PLAN_GROUP_CREATE],
        business_area,
        program=program,
    )

    with CaptureQueriesContext(connection) as miss_ctx:
        first = client.get(_list_url(business_area.slug, program.code))
    assert first.status_code == status.HTTP_200_OK
    etag_before = first.headers["etag"]

    with CaptureQueriesContext(connection) as hit_ctx:
        cached = client.get(_list_url(business_area.slug, program.code))
    assert cached.status_code == status.HTTP_200_OK
    assert cached.headers["etag"] == etag_before
    assert len(hit_ctx.captured_queries) == 4
    assert len(miss_ctx.captured_queries) == 13

    with TestCase.captureOnCommitCallbacks(execute=True):
        client.post(_list_url(business_area.slug, program.code), {"name": "New Group", "cycle": str(cycle.id)})

    with CaptureQueriesContext(connection) as invalidated_ctx:
        second = client.get(_list_url(business_area.slug, program.code))
    assert second.status_code == status.HTTP_200_OK
    assert second.headers["etag"] != etag_before
    assert len(invalidated_ctx.captured_queries) == 7


def test_list_cache_invalidated_on_group_rename(
    client: Any,
    user: Any,
    business_area: Any,
    program: Any,
    cycle: Any,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PM_PAYMENT_PLAN_GROUP_VIEW_LIST, Permissions.PM_PAYMENT_PLAN_GROUP_UPDATE],
        business_area,
        program=program,
    )

    group = cycle.payment_plan_groups.first()

    with CaptureQueriesContext(connection) as miss_ctx:
        first = client.get(_list_url(business_area.slug, program.code))
    assert first.status_code == status.HTTP_200_OK
    etag_before = first.headers["etag"]

    with CaptureQueriesContext(connection) as hit_ctx:
        cached = client.get(_list_url(business_area.slug, program.code))
    assert cached.status_code == status.HTTP_200_OK
    assert cached.headers["etag"] == etag_before
    assert len(hit_ctx.captured_queries) == 4
    assert len(miss_ctx.captured_queries) == 13

    with TestCase.captureOnCommitCallbacks(execute=True):
        client.put(_detail_url(business_area.slug, program.code, group.id), {"name": "Renamed"})

    with CaptureQueriesContext(connection) as invalidated_ctx:
        second = client.get(_list_url(business_area.slug, program.code))
    assert second.status_code == status.HTTP_200_OK
    assert second.headers["etag"] != etag_before
    assert len(invalidated_ctx.captured_queries) == 7


def test_list_cache_invalidated_on_group_delete(
    client: Any,
    user: Any,
    business_area: Any,
    program: Any,
    cycle: Any,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PM_PAYMENT_PLAN_GROUP_VIEW_LIST, Permissions.PM_PAYMENT_PLAN_GROUP_DELETE],
        business_area,
        program=program,
    )

    group = PaymentPlanGroupFactory(cycle=cycle)

    with CaptureQueriesContext(connection) as miss_ctx:
        first = client.get(_list_url(business_area.slug, program.code))
    assert first.status_code == status.HTTP_200_OK
    etag_before = first.headers["etag"]

    with CaptureQueriesContext(connection) as hit_ctx:
        cached = client.get(_list_url(business_area.slug, program.code))
    assert cached.status_code == status.HTTP_200_OK
    assert cached.headers["etag"] == etag_before
    assert len(hit_ctx.captured_queries) == 4
    assert len(miss_ctx.captured_queries) == 13

    with TestCase.captureOnCommitCallbacks(execute=True):
        client.delete(_detail_url(business_area.slug, program.code, group.id))

    with CaptureQueriesContext(connection) as invalidated_ctx:
        second = client.get(_list_url(business_area.slug, program.code))
    assert second.status_code == status.HTTP_200_OK
    assert second.headers["etag"] != etag_before
    assert len(invalidated_ctx.captured_queries) == 7


def test_list_ordering_by_name_ascending(
    client: Any,
    user: Any,
    business_area: Any,
    program: Any,
    cycle: Any,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        user, [Permissions.PM_PAYMENT_PLAN_GROUP_VIEW_LIST], business_area, program=program
    )

    PaymentPlanGroupFactory(cycle=cycle, name="Zebra")
    PaymentPlanGroupFactory(cycle=cycle, name="Alpha")

    response = client.get(_list_url(business_area.slug, program.code), {"ordering": "name"})

    assert response.status_code == status.HTTP_200_OK
    names = [r["name"] for r in response.json()["results"]]
    assert names == sorted(names)


def test_list_ordering_by_name_descending(
    client: Any,
    user: Any,
    business_area: Any,
    program: Any,
    cycle: Any,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        user, [Permissions.PM_PAYMENT_PLAN_GROUP_VIEW_LIST], business_area, program=program
    )

    PaymentPlanGroupFactory(cycle=cycle, name="Zebra")
    PaymentPlanGroupFactory(cycle=cycle, name="Alpha")

    response = client.get(_list_url(business_area.slug, program.code), {"ordering": "-name"})

    assert response.status_code == status.HTTP_200_OK
    names = [r["name"] for r in response.json()["results"]]
    assert names == sorted(names, reverse=True)


def test_list_ordering_by_created_at_descending(
    client: Any,
    user: Any,
    business_area: Any,
    program: Any,
    cycle: Any,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        user, [Permissions.PM_PAYMENT_PLAN_GROUP_VIEW_LIST], business_area, program=program
    )

    first = PaymentPlanGroupFactory(cycle=cycle, name="First")
    second = PaymentPlanGroupFactory(cycle=cycle, name="Second")

    response = client.get(_list_url(business_area.slug, program.code), {"ordering": "-created_at"})

    assert response.status_code == status.HTTP_200_OK
    ids = [r["id"] for r in response.json()["results"]]
    assert ids.index(str(second.id)) < ids.index(str(first.id))


def test_list_ordering_by_cycle_title_ascending(
    client: Any,
    user: Any,
    business_area: Any,
    program: Any,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        user, [Permissions.PM_PAYMENT_PLAN_GROUP_VIEW_LIST], business_area, program=program
    )

    cycle_b = ProgramCycleFactory(program=program, title="Cycle B")
    cycle_a = ProgramCycleFactory(program=program, title="Cycle A")
    group_b = cycle_b.payment_plan_groups.first()
    group_a = cycle_a.payment_plan_groups.first()

    response = client.get(_list_url(business_area.slug, program.code), {"ordering": "cycle"})

    assert response.status_code == status.HTTP_200_OK
    ids = [r["id"] for r in response.json()["results"]]
    assert ids.index(str(group_a.id)) < ids.index(str(group_b.id))


def test_list_ordering_by_cycle_title_descending(
    client: Any,
    user: Any,
    business_area: Any,
    program: Any,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        user, [Permissions.PM_PAYMENT_PLAN_GROUP_VIEW_LIST], business_area, program=program
    )

    cycle_b = ProgramCycleFactory(program=program, title="Cycle B")
    cycle_a = ProgramCycleFactory(program=program, title="Cycle A")
    group_b = cycle_b.payment_plan_groups.first()
    group_a = cycle_a.payment_plan_groups.first()

    response = client.get(_list_url(business_area.slug, program.code), {"ordering": "-cycle"})

    assert response.status_code == status.HTTP_200_OK
    ids = [r["id"] for r in response.json()["results"]]
    assert ids.index(str(group_b.id)) < ids.index(str(group_a.id))


def test_search_by_name(
    client: Any,
    user: Any,
    business_area: Any,
    program: Any,
    cycle: Any,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        user, [Permissions.PM_PAYMENT_PLAN_GROUP_VIEW_LIST], business_area, program=program
    )
    group = PaymentPlanGroupFactory(cycle=cycle, name="Alpha Group")
    other = PaymentPlanGroupFactory(cycle=cycle, name="Beta Group")

    response = client.get(_list_url(business_area.slug, program.code), {"search": "Alpha"})

    assert response.status_code == status.HTTP_200_OK
    results = response.json()["results"]
    returned_ids = {r["id"] for r in results}
    assert str(group.id) in returned_ids
    assert str(other.id) not in returned_ids


def test_search_by_unicef_id(
    client: Any,
    user: Any,
    business_area: Any,
    program: Any,
    cycle: Any,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        user, [Permissions.PM_PAYMENT_PLAN_GROUP_VIEW_LIST], business_area, program=program
    )
    group = PaymentPlanGroupFactory(cycle=cycle)
    other = PaymentPlanGroupFactory(cycle=cycle)
    PaymentPlanGroup.objects.filter(pk=group.pk).update(unicef_id="GRP-FIND-ME")

    response = client.get(_list_url(business_area.slug, program.code), {"search": "FIND-ME"})

    assert response.status_code == status.HTTP_200_OK
    results = response.json()["results"]
    returned_ids = {r["id"] for r in results}
    assert str(group.id) in returned_ids
    assert str(other.id) not in returned_ids
