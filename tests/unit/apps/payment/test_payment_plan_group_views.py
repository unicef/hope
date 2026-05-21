from decimal import Decimal
from io import BytesIO
from typing import Any, Callable
from unittest import mock
from unittest.mock import patch
from zipfile import BadZipFile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import connection
from django.test import TestCase
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
import openpyxl
import pytest
from rest_framework import status

from extras.test_utils.factories import (
    BusinessAreaFactory,
    FileTempFactory,
    PaymentFactory,
    PaymentPlanFactory,
    PaymentPlanGroupFactory,
    PaymentPlanSplitFactory,
    ProgramCycleFactory,
    ProgramFactory,
    UserFactory,
)
from extras.test_utils.factories.payment import (
    DeliveryMechanismFactory,
    FinancialServiceProviderFactory,
    FinancialServiceProviderXlsxTemplateFactory,
    FspXlsxTemplatePerDeliveryMechanismFactory,
    PaymentHouseholdSnapshotFactory,
)
from hope.apps.account.permissions import Permissions
from hope.apps.core.celery_tasks import async_retry_job_task
from hope.apps.payment.api.serializers import PaymentPlanGroupDetailSerializer
from hope.apps.payment.xlsx.xlsx_error import XlsxError
from hope.models import AsyncRetryJob, PaymentPlan, PaymentPlanGroup

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


def _export_url(ba_slug: str, program_code: str, group_id: Any) -> str:
    return reverse(
        "api:payments:payment-plan-groups-delivery-export-xlsx",
        kwargs={"business_area_slug": ba_slug, "program_code": program_code, "pk": group_id},
    )


def _import_url(ba_slug: str, program_code: str, group_id: Any) -> str:
    return reverse(
        "api:payments:payment-plan-groups-delivery-import-xlsx",
        kwargs={"business_area_slug": ba_slug, "program_code": program_code, "pk": group_id},
    )


@pytest.fixture
def second_cycle_in_program(cycle: Any) -> Any:
    return ProgramCycleFactory(program=cycle.program)


@pytest.fixture
def extra_group_in_cycle(cycle: Any) -> Any:
    return PaymentPlanGroupFactory(cycle=cycle)


@pytest.fixture
def existing_named_group_in_cycle(cycle: Any) -> Any:
    return PaymentPlanGroupFactory(cycle=cycle, name="Existing Group")


@pytest.fixture
def taken_named_group_in_cycle(cycle: Any) -> Any:
    return PaymentPlanGroupFactory(cycle=cycle, name="Taken Name")


@pytest.fixture
def shared_named_group_in_other_cycle(program: Any) -> Any:
    other_cycle = ProgramCycleFactory(program=program)
    return PaymentPlanGroupFactory(cycle=other_cycle, name="Shared Name")


@pytest.fixture
def group_with_two_aggregated_plans(business_area: Any, cycle: Any) -> Any:
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
    return group


@pytest.fixture
def group_with_plan(business_area: Any, cycle: Any) -> Any:
    group = cycle.payment_plan_groups.first()
    PaymentPlanFactory(business_area=business_area, program_cycle=cycle, payment_plan_group=group)
    return group


@pytest.fixture
def group_with_accepted_plan(business_area: Any, cycle: Any) -> Any:
    group = cycle.payment_plan_groups.first()
    PaymentPlanFactory(
        business_area=business_area,
        program_cycle=cycle,
        payment_plan_group=group,
        status=PaymentPlan.Status.ACCEPTED,
    )
    return group


@pytest.fixture
def group_with_accepted_plan_and_payment(business_area: Any, cycle: Any) -> Any:
    group = cycle.payment_plan_groups.first()
    plan = PaymentPlanFactory(
        business_area=business_area,
        program_cycle=cycle,
        payment_plan_group=group,
        status=PaymentPlan.Status.ACCEPTED,
    )
    PaymentFactory(parent=plan)
    return group


@pytest.fixture
def group_with_locked_plan(business_area: Any, cycle: Any) -> Any:
    group = cycle.payment_plan_groups.first()
    PaymentPlanFactory(
        business_area=business_area,
        program_cycle=cycle,
        payment_plan_group=group,
        status=PaymentPlan.Status.LOCKED,
    )
    return group


@pytest.fixture
def other_business_area_cycle() -> Any:
    other_ba = BusinessAreaFactory(slug="other-ba")
    other_program = ProgramFactory(business_area=other_ba)
    return ProgramCycleFactory(program=other_program)


@pytest.fixture
def groups_for_name_search(cycle: Any) -> dict:
    alpha = PaymentPlanGroupFactory(cycle=cycle, name="Alpha Group")
    beta = PaymentPlanGroupFactory(cycle=cycle, name="Beta Group")
    return {"alpha": alpha, "beta": beta}


@pytest.fixture
def groups_for_unicef_id_search(cycle: Any) -> dict:
    target = PaymentPlanGroupFactory(cycle=cycle)
    other = PaymentPlanGroupFactory(cycle=cycle)
    PaymentPlanGroup.objects.filter(pk=target.pk).update(unicef_id="GRP-FIND-ME")
    target.refresh_from_db()
    return {"target": target, "other": other}


@pytest.fixture
def two_named_groups_zebra_alpha(cycle: Any) -> dict:
    zebra = PaymentPlanGroupFactory(cycle=cycle, name="Zebra")
    alpha = PaymentPlanGroupFactory(cycle=cycle, name="Alpha")
    return {"zebra": zebra, "alpha": alpha}


@pytest.fixture
def two_named_groups_first_second(cycle: Any) -> dict:
    first = PaymentPlanGroupFactory(cycle=cycle, name="First")
    second = PaymentPlanGroupFactory(cycle=cycle, name="Second")
    return {"first": first, "second": second}


@pytest.fixture
def two_cycles_a_b(program: Any) -> dict:
    cycle_b = ProgramCycleFactory(program=program, title="Cycle B")
    cycle_a = ProgramCycleFactory(program=program, title="Cycle A")
    return {"cycle_a": cycle_a, "cycle_b": cycle_b}


@pytest.fixture
def e2e_import_setup(business_area: Any, cycle: Any) -> dict:
    fsp_one = FinancialServiceProviderFactory(name="E2E FSP One", vision_vendor_number="999111111")
    fsp_two = FinancialServiceProviderFactory(name="E2E FSP Two", vision_vendor_number="999222222")
    dm_one = DeliveryMechanismFactory(code="e2e-cash", name="E2ECash", payment_gateway_id="e2e-cash")
    dm_two = DeliveryMechanismFactory(code="e2e-voucher", name="E2EVoucher", payment_gateway_id="e2e-voucher")
    FspXlsxTemplatePerDeliveryMechanismFactory(
        financial_service_provider=fsp_one,
        delivery_mechanism=dm_one,
        xlsx_template=FinancialServiceProviderXlsxTemplateFactory(columns=["payment_id", "delivered_quantity"]),
    )
    FspXlsxTemplatePerDeliveryMechanismFactory(
        financial_service_provider=fsp_two,
        delivery_mechanism=dm_two,
        xlsx_template=FinancialServiceProviderXlsxTemplateFactory(columns=["payment_id", "delivered_quantity"]),
    )
    group = cycle.payment_plan_groups.first()
    plan_one = PaymentPlanFactory(
        business_area=business_area,
        program_cycle=cycle,
        payment_plan_group=group,
        status=PaymentPlan.Status.ACCEPTED,
        financial_service_provider=fsp_one,
        delivery_mechanism=dm_one,
        exchange_rate=Decimal("1.0"),
        custom_exchange_rate=True,
    )
    plan_two = PaymentPlanFactory(
        business_area=business_area,
        program_cycle=cycle,
        payment_plan_group=group,
        status=PaymentPlan.Status.ACCEPTED,
        financial_service_provider=fsp_two,
        delivery_mechanism=dm_two,
        exchange_rate=Decimal("1.0"),
        custom_exchange_rate=True,
    )
    payment_one = PaymentFactory(
        parent=plan_one,
        financial_service_provider=fsp_one,
        delivery_type=dm_one,
        program=plan_one.program,
        entitlement_quantity=Decimal("100.00"),
        entitlement_quantity_usd=Decimal("10.00"),
        delivered_quantity=Decimal("50.00"),
    )
    PaymentHouseholdSnapshotFactory(payment=payment_one, snapshot_data={})
    payment_two = PaymentFactory(
        parent=plan_two,
        financial_service_provider=fsp_two,
        delivery_type=dm_two,
        program=plan_two.program,
        entitlement_quantity=Decimal("200.00"),
        entitlement_quantity_usd=Decimal("20.00"),
        delivered_quantity=Decimal("50.00"),
    )
    PaymentHouseholdSnapshotFactory(payment=payment_two, snapshot_data={})
    return {"group": group, "payment_one": payment_one, "payment_two": payment_two}


def test_list_groups_for_cycle(
    client: Any,
    user: Any,
    business_area: Any,
    program: Any,
    cycle: Any,
    second_cycle_in_program: Any,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        user, [Permissions.PM_PAYMENT_PLAN_GROUP_VIEW_LIST], business_area, program=program
    )

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
    second_cycle_in_program: Any,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        user, [Permissions.PM_PAYMENT_PLAN_GROUP_VIEW_LIST], business_area, program=program
    )

    # cycle auto-creates 1 group; second cycle auto-creates another
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
    second_cycle_in_program: Any,
    extra_group_in_cycle: Any,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        user, [Permissions.PM_PAYMENT_PLAN_GROUP_VIEW_LIST], business_area, program=program
    )

    response = client.get(_count_url(business_area.slug, program.code), {"cycle": str(cycle.id)})

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["count"] == 2  # default group + one added


def test_count_groups_no_cycle_filter(
    client: Any,
    user: Any,
    business_area: Any,
    program: Any,
    cycle: Any,
    second_cycle_in_program: Any,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        user, [Permissions.PM_PAYMENT_PLAN_GROUP_VIEW_LIST], business_area, program=program
    )

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
    existing_named_group_in_cycle: Any,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(user, [Permissions.PM_PAYMENT_PLAN_GROUP_CREATE], business_area, program=program)

    response = client.post(
        _list_url(business_area.slug, program.code),
        {"name": existing_named_group_in_cycle.name, "cycle": str(cycle.id)},
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["name"][0] == "A group named 'Existing Group' already exists in this cycle."


def test_create_group_same_name_different_cycle_allowed(
    client: Any,
    user: Any,
    business_area: Any,
    program: Any,
    cycle: Any,
    shared_named_group_in_other_cycle: Any,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(user, [Permissions.PM_PAYMENT_PLAN_GROUP_CREATE], business_area, program=program)

    response = client.post(
        _list_url(business_area.slug, program.code),
        {"name": shared_named_group_in_other_cycle.name, "cycle": str(cycle.id)},
    )

    assert response.status_code == status.HTTP_201_CREATED


def test_retrieve_detail_aggregated_totals(
    client: Any,
    user: Any,
    business_area: Any,
    program: Any,
    group_with_two_aggregated_plans: Any,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        user, [Permissions.PM_PAYMENT_PLAN_GROUP_VIEW_DETAIL], business_area, program=program
    )

    response = client.get(_detail_url(business_area.slug, program.code, group_with_two_aggregated_plans.id))

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
    extra_group_in_cycle: Any,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(user, [Permissions.PM_PAYMENT_PLAN_GROUP_DELETE], business_area, program=program)

    # delete the extra group (the default group is kept)
    response = client.delete(_detail_url(business_area.slug, program.code, extra_group_in_cycle.id))

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not PaymentPlanGroup.objects.filter(id=extra_group_in_cycle.id).exists()


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
    group_with_plan: Any,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(user, [Permissions.PM_PAYMENT_PLAN_GROUP_DELETE], business_area, program=program)

    response = client.delete(_detail_url(business_area.slug, program.code, group_with_plan.id))

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()[0] == "Cannot delete a group that has payment plans."
    assert PaymentPlanGroup.objects.filter(id=group_with_plan.id).exists()


def test_list_excludes_other_business_area(
    client: Any,
    user: Any,
    business_area: Any,
    program: Any,
    cycle: Any,
    other_business_area_cycle: Any,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        user, [Permissions.PM_PAYMENT_PLAN_GROUP_VIEW_LIST], business_area, program=program
    )

    # cycle auto-creates 1 group in business_area; other_business_area_cycle adds another in a different BA
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
    extra_group_in_cycle: Any,
    create_user_role_with_permissions: Any,
    permissions: list,
    expected_status: int,
) -> None:
    create_user_role_with_permissions(user, permissions, business_area, program=program)

    response = client.delete(_detail_url(business_area.slug, program.code, extra_group_in_cycle.id))

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
    taken_named_group_in_cycle: Any,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(user, [Permissions.PM_PAYMENT_PLAN_GROUP_UPDATE], business_area, program=program)

    group = cycle.payment_plan_groups.exclude(pk=taken_named_group_in_cycle.pk).first()

    response = client.put(
        _detail_url(business_area.slug, program.code, group.id),
        {"name": taken_named_group_in_cycle.name},
    )

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
    shared_named_group_in_other_cycle: Any,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(user, [Permissions.PM_PAYMENT_PLAN_GROUP_UPDATE], business_area, program=program)

    group = cycle.payment_plan_groups.first()

    response = client.put(
        _detail_url(business_area.slug, program.code, group.id),
        {"name": shared_named_group_in_other_cycle.name},
    )

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
    extra_group_in_cycle: Any,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PM_PAYMENT_PLAN_GROUP_VIEW_LIST, Permissions.PM_PAYMENT_PLAN_GROUP_DELETE],
        business_area,
        program=program,
    )

    group = extra_group_in_cycle

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


@pytest.mark.parametrize(
    ("ordering", "reverse"),
    [("name", False), ("-name", True)],
)
def test_list_ordering_by_name(
    client: Any,
    user: Any,
    business_area: Any,
    program: Any,
    two_named_groups_zebra_alpha: Any,
    create_user_role_with_permissions: Any,
    ordering: str,
    reverse: bool,
) -> None:
    create_user_role_with_permissions(
        user, [Permissions.PM_PAYMENT_PLAN_GROUP_VIEW_LIST], business_area, program=program
    )

    response = client.get(_list_url(business_area.slug, program.code), {"ordering": ordering})

    assert response.status_code == status.HTTP_200_OK
    names = [r["name"] for r in response.json()["results"]]
    assert names == sorted(names, reverse=reverse)


def test_list_ordering_by_created_at_descending(
    client: Any,
    user: Any,
    business_area: Any,
    program: Any,
    two_named_groups_first_second: Any,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        user, [Permissions.PM_PAYMENT_PLAN_GROUP_VIEW_LIST], business_area, program=program
    )

    response = client.get(_list_url(business_area.slug, program.code), {"ordering": "-created_at"})

    assert response.status_code == status.HTTP_200_OK
    ids = [r["id"] for r in response.json()["results"]]
    assert ids.index(str(two_named_groups_first_second["second"].id)) < ids.index(
        str(two_named_groups_first_second["first"].id)
    )


@pytest.mark.parametrize(
    ("ordering", "first_key", "second_key"),
    [("cycle", "cycle_a", "cycle_b"), ("-cycle", "cycle_b", "cycle_a")],
)
def test_list_ordering_by_cycle_title(
    client: Any,
    user: Any,
    business_area: Any,
    program: Any,
    two_cycles_a_b: Any,
    create_user_role_with_permissions: Any,
    ordering: str,
    first_key: str,
    second_key: str,
) -> None:
    create_user_role_with_permissions(
        user, [Permissions.PM_PAYMENT_PLAN_GROUP_VIEW_LIST], business_area, program=program
    )
    first_group = two_cycles_a_b[first_key].payment_plan_groups.first()
    second_group = two_cycles_a_b[second_key].payment_plan_groups.first()

    response = client.get(_list_url(business_area.slug, program.code), {"ordering": ordering})

    assert response.status_code == status.HTTP_200_OK
    ids = [r["id"] for r in response.json()["results"]]
    assert ids.index(str(first_group.id)) < ids.index(str(second_group.id))


def test_search_by_name(
    client: Any,
    user: Any,
    business_area: Any,
    program: Any,
    groups_for_name_search: Any,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        user, [Permissions.PM_PAYMENT_PLAN_GROUP_VIEW_LIST], business_area, program=program
    )

    response = client.get(_list_url(business_area.slug, program.code), {"search": "Alpha"})

    assert response.status_code == status.HTTP_200_OK
    results = response.json()["results"]
    returned_ids = {r["id"] for r in results}
    assert str(groups_for_name_search["alpha"].id) in returned_ids
    assert str(groups_for_name_search["beta"].id) not in returned_ids


def test_search_by_unicef_id(
    client: Any,
    user: Any,
    business_area: Any,
    program: Any,
    groups_for_unicef_id_search: Any,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        user, [Permissions.PM_PAYMENT_PLAN_GROUP_VIEW_LIST], business_area, program=program
    )

    response = client.get(_list_url(business_area.slug, program.code), {"search": "FIND-ME"})

    assert response.status_code == status.HTTP_200_OK
    results = response.json()["results"]
    returned_ids = {r["id"] for r in results}
    assert str(groups_for_unicef_id_search["target"].id) in returned_ids
    assert str(groups_for_unicef_id_search["other"].id) not in returned_ids


def test_export_with_correct_permission_returns_200(
    client: Any,
    user: Any,
    business_area: Any,
    program: Any,
    group_with_accepted_plan_and_payment: Any,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        user, [Permissions.PM_PAYMENT_PLAN_GROUP_EXPORT_XLSX], business_area, program=program
    )
    group = group_with_accepted_plan_and_payment

    with patch("hope.apps.payment.api.views.export_payment_plan_group_per_fsp_xlsx_async_task") as mocked_task:
        response = client.post(_export_url(business_area.slug, program.code, group.id))

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == str(group.id)
    mocked_task.assert_not_called()


def test_export_sets_background_action_status_to_exporting(
    client: Any,
    user: Any,
    business_area: Any,
    program: Any,
    group_with_accepted_plan_and_payment: Any,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        user, [Permissions.PM_PAYMENT_PLAN_GROUP_EXPORT_XLSX], business_area, program=program
    )
    group = group_with_accepted_plan_and_payment

    with patch("hope.apps.payment.api.views.export_payment_plan_group_per_fsp_xlsx_async_task"):
        response = client.post(_export_url(business_area.slug, program.code, group.id))

    assert response.status_code == status.HTTP_200_OK
    group.refresh_from_db()
    assert group.background_action_status_export == PaymentPlanGroup.BackgroundExportActionStatus.XLSX_EXPORTING


def test_export_when_already_exporting_returns_400(
    client: Any,
    user: Any,
    business_area: Any,
    program: Any,
    group_with_accepted_plan_and_payment: Any,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        user, [Permissions.PM_PAYMENT_PLAN_GROUP_EXPORT_XLSX], business_area, program=program
    )
    group = group_with_accepted_plan_and_payment
    group.background_action_status_export = PaymentPlanGroup.BackgroundExportActionStatus.XLSX_EXPORTING
    group.save(update_fields=["background_action_status_export"])

    with patch("hope.apps.payment.api.views.export_payment_plan_group_per_fsp_xlsx_async_task") as mocked_task:
        response = client.post(_export_url(business_area.slug, program.code, group.id))

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Export already in progress." in str(response.json())
    mocked_task.assert_not_called()


def test_export_without_accepted_payment_plan_returns_400(
    client: Any,
    user: Any,
    business_area: Any,
    program: Any,
    group_with_locked_plan: Any,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        user, [Permissions.PM_PAYMENT_PLAN_GROUP_EXPORT_XLSX], business_area, program=program
    )
    group = group_with_locked_plan

    with patch("hope.apps.payment.api.views.export_payment_plan_group_per_fsp_xlsx_async_task") as mocked_task:
        response = client.post(_export_url(business_area.slug, program.code, group.id))

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Export requires at least one payment plan in ACCEPTED or FINISHED status." in str(response.json())
    mocked_task.assert_not_called()
    group.refresh_from_db()
    assert group.background_action_status_export is None


def test_export_without_eligible_payments_returns_400(
    client: Any,
    user: Any,
    business_area: Any,
    program: Any,
    group_with_accepted_plan: Any,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        user, [Permissions.PM_PAYMENT_PLAN_GROUP_EXPORT_XLSX], business_area, program=program
    )
    group = group_with_accepted_plan

    with patch("hope.apps.payment.api.views.export_payment_plan_group_per_fsp_xlsx_async_task") as mocked_task:
        response = client.post(_export_url(business_area.slug, program.code, group.id))

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "there are no eligible payments to export." in str(response.json())
    mocked_task.assert_not_called()
    group.refresh_from_db()
    assert group.background_action_status_export is None


def test_export_queues_async_task_on_commit(
    client: Any,
    user: Any,
    business_area: Any,
    program: Any,
    group_with_accepted_plan_and_payment: Any,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        user, [Permissions.PM_PAYMENT_PLAN_GROUP_EXPORT_XLSX], business_area, program=program
    )
    group = group_with_accepted_plan_and_payment

    with (
        patch("hope.apps.payment.api.views.export_payment_plan_group_per_fsp_xlsx_async_task") as mocked_task,
        TestCase.captureOnCommitCallbacks(execute=True),
    ):
        response = client.post(_export_url(business_area.slug, program.code, group.id))

    assert response.status_code == status.HTTP_200_OK
    mocked_task.assert_called_once()
    called_group, called_user_id = mocked_task.call_args[0]
    assert called_group.id == group.id
    assert called_user_id == str(user.pk)


def test_export_rejected_for_group_in_other_business_area(
    client: Any,
    user: Any,
    business_area: Any,
    program: Any,
    other_business_area_cycle: Any,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        user, [Permissions.PM_PAYMENT_PLAN_GROUP_EXPORT_XLSX], business_area, program=program
    )
    other_group = other_business_area_cycle.payment_plan_groups.first()

    with patch("hope.apps.payment.api.views.export_payment_plan_group_per_fsp_xlsx_async_task"):
        response = client.post(_export_url(business_area.slug, program.code, other_group.id))

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.parametrize(
    ("permissions", "expected_status"),
    [
        ([Permissions.PM_PAYMENT_PLAN_GROUP_EXPORT_XLSX], status.HTTP_200_OK),
        ([Permissions.PM_PAYMENT_PLAN_GROUP_VIEW_DETAIL], status.HTTP_403_FORBIDDEN),
        ([Permissions.PM_PAYMENT_PLAN_GROUP_VIEW_LIST], status.HTTP_403_FORBIDDEN),
        ([Permissions.PM_PAYMENT_PLAN_GROUP_CREATE], status.HTTP_403_FORBIDDEN),
        ([Permissions.PM_PAYMENT_PLAN_GROUP_UPDATE], status.HTTP_403_FORBIDDEN),
        ([Permissions.PM_PAYMENT_PLAN_GROUP_DELETE], status.HTTP_403_FORBIDDEN),
        ([], status.HTTP_403_FORBIDDEN),
    ],
)
def test_export_permissions(
    client: Any,
    user: Any,
    business_area: Any,
    program: Any,
    group_with_accepted_plan_and_payment: Any,
    create_user_role_with_permissions: Any,
    permissions: list,
    expected_status: int,
) -> None:
    create_user_role_with_permissions(user, permissions, business_area, program=program)
    group = group_with_accepted_plan_and_payment

    with patch("hope.apps.payment.api.views.export_payment_plan_group_per_fsp_xlsx_async_task"):
        response = client.post(_export_url(business_area.slug, program.code, group.id))

    assert response.status_code == expected_status


def _send_group_to_payment_gateway_url(ba_slug: str, program_code: str, group_id: Any) -> str:
    return reverse(
        "api:payments:payment-plan-groups-send-to-payment-gateway",
        kwargs={"business_area_slug": ba_slug, "program_code": program_code, "pk": group_id},
    )


def test_detail_can_send_to_payment_gateway_true(
    client: Any,
    user: Any,
    business_area: Any,
    program: Any,
    cycle: Any,
    create_user_role_with_permissions: Any,
    create_sendable_payment_plan: Callable,
) -> None:
    create_user_role_with_permissions(
        user, [Permissions.PM_PAYMENT_PLAN_GROUP_VIEW_DETAIL], business_area, program=program
    )
    group = cycle.payment_plan_groups.first()
    create_sendable_payment_plan(cycle, group)

    response = client.get(_detail_url(business_area.slug, program.code, group.id))

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["can_send_to_payment_gateway"] is True


def test_detail_can_send_to_payment_gateway_false_without_sendable_plan(
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
        status=PaymentPlan.Status.OPEN,
    )

    response = client.get(_detail_url(business_area.slug, program.code, group.id))

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["can_send_to_payment_gateway"] is False


@pytest.fixture
def create_sendable_payment_plan(business_area: Any) -> Callable:
    def _create_sendable_payment_plan(cycle: Any, group: Any) -> Any:
        payment_plan = PaymentPlanFactory(
            business_area=business_area,
            program_cycle=cycle,
            payment_plan_group=group,
            status=PaymentPlan.Status.ACCEPTED,
            financial_service_provider=FinancialServiceProviderFactory(),
            use_payment_gateway=True,
        )
        PaymentPlanSplitFactory(payment_plan=payment_plan)
        return payment_plan

    return _create_sendable_payment_plan


def test_send_group_to_payment_gateway_dispatches_each_plan(
    client: Any,
    user: Any,
    business_area: Any,
    program: Any,
    cycle: Any,
    create_user_role_with_permissions: Any,
    create_sendable_payment_plan: Callable,
) -> None:
    create_user_role_with_permissions(
        user, [Permissions.PM_PAYMENT_PLAN_GROUP_SEND_TO_PAYMENT_GATEWAY], business_area, program=program
    )
    group = cycle.payment_plan_groups.first()
    plan_a = create_sendable_payment_plan(cycle, group)
    plan_b = create_sendable_payment_plan(cycle, group)

    with (
        mock.patch(
            "hope.apps.payment.services.payment_plan_services.PaymentPlanService.__init__",
            return_value=None,
        ) as mock_service_init,
        mock.patch(
            "hope.apps.payment.services.payment_plan_services.PaymentPlanService.execute_update_status_action"
        ) as mock_execute_update_status_action,
    ):
        response = client.post(_send_group_to_payment_gateway_url(business_area.slug, program.code, group.id))

    assert response.status_code == status.HTTP_200_OK
    assert mock_execute_update_status_action.call_count == 2
    dispatched_actions = {call.kwargs["input_data"]["action"] for call in mock_execute_update_status_action.mock_calls}
    assert dispatched_actions == {PaymentPlan.Action.SEND_TO_PAYMENT_GATEWAY}

    init_targets = {call.args[0].pk for call in mock_service_init.mock_calls}
    assert init_targets == {plan_a.pk, plan_b.pk}


def test_send_group_to_payment_gateway_with_no_plans_fails(
    client: Any,
    user: Any,
    business_area: Any,
    program: Any,
    cycle: Any,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        user, [Permissions.PM_PAYMENT_PLAN_GROUP_SEND_TO_PAYMENT_GATEWAY], business_area, program=program
    )
    group = PaymentPlanGroupFactory(cycle=cycle, name="Empty Group")

    response = client.post(_send_group_to_payment_gateway_url(business_area.slug, program.code, group.id))

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "No payment plans can be sent" in response.json()[0]


def test_send_group_to_payment_gateway_dispatches_only_sendable_plans(
    client: Any,
    user: Any,
    business_area: Any,
    program: Any,
    cycle: Any,
    create_user_role_with_permissions: Any,
    create_sendable_payment_plan: Callable,
) -> None:
    create_user_role_with_permissions(
        user, [Permissions.PM_PAYMENT_PLAN_GROUP_SEND_TO_PAYMENT_GATEWAY], business_area, program=program
    )
    group = cycle.payment_plan_groups.first()
    sendable = create_sendable_payment_plan(cycle, group)
    PaymentPlanFactory(
        business_area=business_area,
        program_cycle=cycle,
        payment_plan_group=group,
        status=PaymentPlan.Status.OPEN,
    )

    with (
        mock.patch(
            "hope.apps.payment.services.payment_plan_services.PaymentPlanService.__init__",
            return_value=None,
        ) as service_init,
        mock.patch(
            "hope.apps.payment.services.payment_plan_services.PaymentPlanService.execute_update_status_action"
        ) as dispatch,
    ):
        response = client.post(_send_group_to_payment_gateway_url(business_area.slug, program.code, group.id))

    assert response.status_code == status.HTTP_200_OK
    assert dispatch.call_count == 1
    init_targets = {call.args[0].pk for call in service_init.mock_calls}
    assert init_targets == {sendable.pk}


def test_send_group_to_payment_gateway_fails_when_no_plan_is_sendable(
    client: Any,
    user: Any,
    business_area: Any,
    program: Any,
    cycle: Any,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        user, [Permissions.PM_PAYMENT_PLAN_GROUP_SEND_TO_PAYMENT_GATEWAY], business_area, program=program
    )
    group = cycle.payment_plan_groups.first()
    PaymentPlanFactory(
        business_area=business_area,
        program_cycle=cycle,
        payment_plan_group=group,
        status=PaymentPlan.Status.OPEN,
    )

    response = client.post(_send_group_to_payment_gateway_url(business_area.slug, program.code, group.id))

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "No payment plans can be sent" in response.json()[0]


def test_send_group_to_payment_gateway_fails_when_plan_has_no_unsent_splits(
    client: Any,
    user: Any,
    business_area: Any,
    program: Any,
    cycle: Any,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        user, [Permissions.PM_PAYMENT_PLAN_GROUP_SEND_TO_PAYMENT_GATEWAY], business_area, program=program
    )
    group = cycle.payment_plan_groups.first()
    plan = PaymentPlanFactory(
        business_area=business_area,
        program_cycle=cycle,
        payment_plan_group=group,
        status=PaymentPlan.Status.ACCEPTED,
        financial_service_provider=FinancialServiceProviderFactory(),
        use_payment_gateway=True,
    )
    PaymentPlanSplitFactory(payment_plan=plan, sent_to_payment_gateway=True)

    response = client.post(_send_group_to_payment_gateway_url(business_area.slug, program.code, group.id))

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "No payment plans can be sent" in response.json()[0]


def test_send_group_to_payment_gateway_skips_plan_already_being_sent(
    client: Any,
    user: Any,
    business_area: Any,
    program: Any,
    cycle: Any,
    create_user_role_with_permissions: Any,
    create_sendable_payment_plan: Callable,
) -> None:
    create_user_role_with_permissions(
        user, [Permissions.PM_PAYMENT_PLAN_GROUP_SEND_TO_PAYMENT_GATEWAY], business_area, program=program
    )
    group = cycle.payment_plan_groups.first()
    sendable = create_sendable_payment_plan(cycle, group)
    in_progress = create_sendable_payment_plan(cycle, group)
    in_progress.background_action_status = PaymentPlan.BackgroundActionStatus.SEND_TO_PAYMENT_GATEWAY
    in_progress.save(update_fields=("background_action_status",))

    with (
        mock.patch(
            "hope.apps.payment.services.payment_plan_services.PaymentPlanService.__init__",
            return_value=None,
        ) as service_init,
        mock.patch(
            "hope.apps.payment.services.payment_plan_services.PaymentPlanService.execute_update_status_action"
        ) as dispatch,
    ):
        response = client.post(_send_group_to_payment_gateway_url(business_area.slug, program.code, group.id))

    assert response.status_code == status.HTTP_200_OK
    assert dispatch.call_count == 1
    init_targets = {call.args[0].pk for call in service_init.mock_calls}
    assert init_targets == {sendable.pk}


def test_send_group_to_payment_gateway_locks_the_group_object(
    client: Any,
    user: Any,
    business_area: Any,
    program: Any,
    cycle: Any,
    create_user_role_with_permissions: Any,
    create_sendable_payment_plan: Callable,
) -> None:
    create_user_role_with_permissions(
        user, [Permissions.PM_PAYMENT_PLAN_GROUP_SEND_TO_PAYMENT_GATEWAY], business_area, program=program
    )
    group = cycle.payment_plan_groups.first()
    create_sendable_payment_plan(cycle, group)

    with mock.patch("hope.apps.payment.services.payment_plan_services.PaymentPlanService.execute_update_status_action"):
        with CaptureQueriesContext(connection) as ctx:
            response = client.post(_send_group_to_payment_gateway_url(business_area.slug, program.code, group.id))

    assert response.status_code == status.HTTP_200_OK
    assert any("payment_paymentplangroup" in q["sql"] and "FOR UPDATE" in q["sql"] for q in ctx.captured_queries)


@pytest.mark.parametrize(
    ("permissions", "expected_status"),
    [
        ([Permissions.PM_PAYMENT_PLAN_GROUP_SEND_TO_PAYMENT_GATEWAY], status.HTTP_200_OK),
        ([Permissions.PM_PAYMENT_PLAN_GROUP_VIEW_LIST], status.HTTP_403_FORBIDDEN),
        ([], status.HTTP_403_FORBIDDEN),
    ],
)
def test_send_group_to_payment_gateway_permissions(
    client: Any,
    user: Any,
    business_area: Any,
    program: Any,
    cycle: Any,
    create_user_role_with_permissions: Any,
    create_sendable_payment_plan: Callable,
    permissions: list,
    expected_status: int,
) -> None:
    create_user_role_with_permissions(user, permissions, business_area, program=program)
    group = cycle.payment_plan_groups.first()
    create_sendable_payment_plan(cycle, group)

    with mock.patch("hope.apps.payment.services.payment_plan_services.PaymentPlanService.execute_update_status_action"):
        response = client.post(_send_group_to_payment_gateway_url(business_area.slug, program.code, group.id))
    assert response.status_code == expected_status


def test_get_export_file_returns_none_when_no_export_file(cycle: Any) -> None:
    group = cycle.payment_plan_groups.first()
    assert group.export_file_id is None

    result = PaymentPlanGroupDetailSerializer().get_export_file(group)

    assert result is None


def test_get_export_file_returns_url_when_file_exists(cycle: Any) -> None:
    group = cycle.payment_plan_groups.first()
    group.export_file = FileTempFactory()
    group.save(update_fields=["export_file"])

    result = PaymentPlanGroupDetailSerializer().get_export_file(group)

    assert result == group.export_file.file.url


def test_delivery_import_xlsx_returns_400_when_no_file(
    client: Any,
    user: Any,
    business_area: Any,
    program: Any,
    group_with_accepted_plan: Any,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        user, [Permissions.PM_PAYMENT_PLAN_GROUP_IMPORT_XLSX], business_area, program=program
    )

    response = client.post(
        _import_url(business_area.slug, program.code, group_with_accepted_plan.id), {}, format="multipart"
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "file" in response.json()


def test_delivery_import_xlsx_rejects_bad_zip_file(
    client: Any,
    user: Any,
    business_area: Any,
    program: Any,
    group_with_accepted_plan: Any,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        user, [Permissions.PM_PAYMENT_PLAN_GROUP_IMPORT_XLSX], business_area, program=program
    )
    test_file = SimpleUploadedFile("test.xlsx", b"not-a-zip", content_type="application/vnd.ms-excel")

    with patch("hope.apps.payment.api.views.XlsxPaymentPlanGroupImportPerFspService") as mock_cls:
        mock_cls.return_value.open_workbook.side_effect = BadZipFile("not a zip")
        response = client.post(
            _import_url(business_area.slug, program.code, group_with_accepted_plan.id),
            {"file": test_file},
            format="multipart",
        )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Wrong file type or password protected" in str(response.json())


def test_delivery_import_xlsx_returns_400_on_validation_errors(
    client: Any,
    user: Any,
    business_area: Any,
    program: Any,
    group_with_accepted_plan: Any,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        user, [Permissions.PM_PAYMENT_PLAN_GROUP_IMPORT_XLSX], business_area, program=program
    )
    test_file = SimpleUploadedFile("test.xlsx", b"abc", content_type="application/vnd.ms-excel")

    with patch("hope.apps.payment.api.views.XlsxPaymentPlanGroupImportPerFspService") as mock_cls:
        instance = mock_cls.return_value
        instance.errors = [XlsxError(sheet="Sheet", coordinates="B2", message="Missing column")]
        response = client.post(
            _import_url(business_area.slug, program.code, group_with_accepted_plan.id),
            {"file": test_file},
            format="multipart",
        )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    body = response.json()
    assert body[0]["sheet"] == "Sheet"
    assert body[0]["message"] == "Missing column"


def test_delivery_import_xlsx_succeeds(
    client: Any,
    user: Any,
    business_area: Any,
    program: Any,
    group_with_accepted_plan: Any,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        user, [Permissions.PM_PAYMENT_PLAN_GROUP_IMPORT_XLSX], business_area, program=program
    )
    group = group_with_accepted_plan
    test_file = SimpleUploadedFile("test.xlsx", b"abc", content_type="application/vnd.ms-excel")

    with (
        patch("hope.apps.payment.api.views.XlsxPaymentPlanGroupImportPerFspService") as mock_cls,
        patch("hope.apps.payment.api.views.import_payment_plan_group_per_fsp_from_xlsx_async_task") as mocked_task,
    ):
        mock_cls.return_value.errors = []
        response = client.post(
            _import_url(business_area.slug, program.code, group.id),
            {"file": test_file},
            format="multipart",
        )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == str(group.id)
    group.refresh_from_db()
    assert (
        group.background_action_status_import
        == PaymentPlanGroup.BackgroundImportActionStatus.XLSX_IMPORTING_RECONCILIATION
    )
    assert group.delivery_import_file_id is not None
    mocked_task.assert_not_called()


def test_delivery_import_xlsx_when_already_importing_returns_400(
    client: Any,
    user: Any,
    business_area: Any,
    program: Any,
    group_with_accepted_plan: Any,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        user, [Permissions.PM_PAYMENT_PLAN_GROUP_IMPORT_XLSX], business_area, program=program
    )
    group = group_with_accepted_plan
    group.background_action_status_import = PaymentPlanGroup.BackgroundImportActionStatus.XLSX_IMPORTING_RECONCILIATION
    group.save(update_fields=["background_action_status_import"])
    test_file = SimpleUploadedFile("test.xlsx", b"abc", content_type="application/vnd.ms-excel")

    response = client.post(
        _import_url(business_area.slug, program.code, group.id),
        {"file": test_file},
        format="multipart",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Import already in progress." in str(response.json())


def test_delivery_import_xlsx_without_accepted_plan_returns_400(
    client: Any,
    user: Any,
    business_area: Any,
    program: Any,
    group_with_locked_plan: Any,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        user, [Permissions.PM_PAYMENT_PLAN_GROUP_IMPORT_XLSX], business_area, program=program
    )
    test_file = SimpleUploadedFile("test.xlsx", b"abc", content_type="application/vnd.ms-excel")

    response = client.post(
        _import_url(business_area.slug, program.code, group_with_locked_plan.id),
        {"file": test_file},
        format="multipart",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Import requires at least one payment plan in ACCEPTED or FINISHED status." in str(response.json())


def test_delivery_import_xlsx_queues_async_task_on_commit(
    client: Any,
    user: Any,
    business_area: Any,
    program: Any,
    group_with_accepted_plan: Any,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        user, [Permissions.PM_PAYMENT_PLAN_GROUP_IMPORT_XLSX], business_area, program=program
    )
    group = group_with_accepted_plan
    test_file = SimpleUploadedFile("test.xlsx", b"abc", content_type="application/vnd.ms-excel")

    with (
        patch("hope.apps.payment.api.views.XlsxPaymentPlanGroupImportPerFspService") as mock_cls,
        patch("hope.apps.payment.api.views.import_payment_plan_group_per_fsp_from_xlsx_async_task") as mocked_task,
        TestCase.captureOnCommitCallbacks(execute=True),
    ):
        mock_cls.return_value.errors = []
        response = client.post(
            _import_url(business_area.slug, program.code, group.id),
            {"file": test_file},
            format="multipart",
        )

    assert response.status_code == status.HTTP_200_OK
    mocked_task.assert_called_once()
    (called_group,) = mocked_task.call_args[0]
    assert called_group.id == group.id


@pytest.mark.parametrize(
    ("permissions", "expected_status"),
    [
        ([Permissions.PM_PAYMENT_PLAN_GROUP_IMPORT_XLSX], status.HTTP_200_OK),
        ([Permissions.PM_PAYMENT_PLAN_GROUP_EXPORT_XLSX], status.HTTP_403_FORBIDDEN),
        ([Permissions.PM_PAYMENT_PLAN_GROUP_VIEW_DETAIL], status.HTTP_403_FORBIDDEN),
        ([], status.HTTP_403_FORBIDDEN),
    ],
)
def test_delivery_import_xlsx_permissions(
    client: Any,
    user: Any,
    business_area: Any,
    program: Any,
    group_with_accepted_plan: Any,
    create_user_role_with_permissions: Any,
    permissions: list,
    expected_status: int,
) -> None:
    create_user_role_with_permissions(user, permissions, business_area, program=program)
    test_file = SimpleUploadedFile("test.xlsx", b"abc", content_type="application/vnd.ms-excel")

    with (
        patch("hope.apps.payment.api.views.XlsxPaymentPlanGroupImportPerFspService") as mock_cls,
        patch("hope.apps.payment.api.views.import_payment_plan_group_per_fsp_from_xlsx_async_task"),
    ):
        mock_cls.return_value.errors = []
        response = client.post(
            _import_url(business_area.slug, program.code, group_with_accepted_plan.id),
            {"file": test_file},
            format="multipart",
        )

    assert response.status_code == expected_status


def test_delivery_import_xlsx_end_to_end_updates_payment_data(
    client: Any,
    user: Any,
    business_area: Any,
    program: Any,
    e2e_import_setup: Any,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        user, [Permissions.PM_PAYMENT_PLAN_GROUP_IMPORT_XLSX], business_area, program=program
    )
    group = e2e_import_setup["group"]
    payment_one = e2e_import_setup["payment_one"]
    payment_two = e2e_import_setup["payment_two"]

    workbook = openpyxl.Workbook()
    ws = workbook.active
    ws.append(["payment_id", "delivered_quantity"])
    ws.append([str(payment_one.unicef_id), Decimal("75.00")])
    ws.append([str(payment_two.unicef_id), Decimal("125.00")])
    buffer = BytesIO()
    workbook.save(buffer)
    buffer.seek(0)
    upload = SimpleUploadedFile(
        "import.xlsx",
        buffer.getvalue(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

    with (
        patch("hope.apps.payment.celery_tasks.AsyncRetryJob.queue", autospec=True),
        TestCase.captureOnCommitCallbacks(execute=True),
    ):
        response = client.post(
            _import_url(business_area.slug, program.code, group.id),
            {"file": upload},
            format="multipart",
        )

    assert response.status_code == status.HTTP_200_OK
    group.refresh_from_db()
    assert (
        group.background_action_status_import
        == PaymentPlanGroup.BackgroundImportActionStatus.XLSX_IMPORTING_RECONCILIATION
    )

    job = AsyncRetryJob.objects.latest("pk")
    async_retry_job_task.run(job._meta.label_lower, job.pk, job.version)

    payment_one.refresh_from_db()
    payment_two.refresh_from_db()
    group.refresh_from_db()
    assert payment_one.delivered_quantity == Decimal("75.00")
    assert payment_two.delivered_quantity == Decimal("125.00")
    assert group.background_action_status_import is None
