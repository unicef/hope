from datetime import timezone as dt_timezone
import json
from typing import Any, Callable
from unittest.mock import MagicMock, patch

from django.core.cache import cache
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.utils import timezone
import pytest
from rest_framework import status
from rest_framework.reverse import reverse

from extras.test_utils.factories import (
    BusinessAreaFactory,
    DeliveryMechanismFactory,
    FinancialServiceProviderFactory,
    HouseholdFactory,
    PartnerFactory,
    PaymentFactory,
    PaymentPlanFactory,
    ProgramCycleFactory,
    ProgramFactory,
    RuleCommitFactory,
    UserFactory,
)
from hope.apps.account.permissions import Permissions
from hope.models import Payment, PaymentPlan, Program, ProgramCycle, Rule

pytestmark = pytest.mark.django_db


@pytest.fixture
def business_area() -> Any:
    return BusinessAreaFactory(slug="afghanistan")


@pytest.fixture
def target_population_list_context(
    api_client: Callable,
    business_area: Any,
) -> dict[str, Any]:
    partner = PartnerFactory(name="unittest")
    user = UserFactory(partner=partner)
    program_active = ProgramFactory(business_area=business_area, status=Program.ACTIVE)
    cycle = ProgramCycleFactory(program=program_active, title="Cycle TP List")
    tp = PaymentPlanFactory(
        name="Test new TP",
        business_area=business_area,
        program_cycle=cycle,
        status=PaymentPlan.Status.TP_OPEN,
        created_by=user,
    )
    pp = PaymentPlanFactory(
        business_area=business_area,
        program_cycle=cycle,
        status=PaymentPlan.Status.LOCKED_FSP,
        created_by=user,
    )
    tp_list_url = reverse(
        "api:payments:target-populations-list",
        kwargs={
            "business_area_slug": business_area.slug,
            "program_slug": program_active.slug,
        },
    )
    tp_count_url = reverse(
        "api:payments:target-populations-count",
        kwargs={
            "business_area_slug": business_area.slug,
            "program_slug": program_active.slug,
        },
    )
    client = api_client(user)
    return {
        "business_area": business_area,
        "partner": partner,
        "user": user,
        "client": client,
        "program_active": program_active,
        "cycle": cycle,
        "tp": tp,
        "pp": pp,
        "tp_list_url": tp_list_url,
        "tp_count_url": tp_count_url,
    }


@pytest.fixture
def target_population_detail_context(
    api_client: Callable,
    business_area: Any,
) -> dict[str, Any]:
    partner = PartnerFactory(name="unittest")
    user = UserFactory(partner=partner)
    program_active = ProgramFactory(business_area=business_area, status=Program.ACTIVE)
    cycle = ProgramCycleFactory(program=program_active, title="Cycle TP Detail")

    tp = PaymentPlanFactory(
        business_area=business_area,
        program_cycle=cycle,
        status=PaymentPlan.Status.TP_LOCKED,
        created_by=user,
        name="TP Detail",
    )
    tp_detail_url = reverse(
        "api:payments:target-populations-detail",
        kwargs={
            "business_area_slug": business_area.slug,
            "program_slug": program_active.slug,
            "pk": str(tp.id),
        },
    )
    client = api_client(user)
    return {
        "business_area": business_area,
        "partner": partner,
        "user": user,
        "client": client,
        "program_active": program_active,
        "cycle": cycle,
        "tp": tp,
        "tp_detail_url": tp_detail_url,
    }


@pytest.fixture
def target_population_filter_context(
    api_client: Callable,
    business_area: Any,
    create_user_role_with_permissions: Any,
) -> dict[str, Any]:
    partner = PartnerFactory(name="unittest")
    user = UserFactory(partner=partner)
    program_active = ProgramFactory(business_area=business_area, status=Program.ACTIVE)
    cycle = ProgramCycleFactory(program=program_active, title="Cycle TP Filter")

    tp = PaymentPlanFactory(
        name="OPEN",
        business_area=business_area,
        program_cycle=cycle,
        status=PaymentPlan.Status.TP_OPEN,
        created_by=user,
        total_households_count=999,
    )
    tp_locked = PaymentPlanFactory(
        name="LOCKED",
        business_area=business_area,
        program_cycle=cycle,
        status=PaymentPlan.Status.TP_LOCKED,
        created_by=user,
        total_households_count=888,
    )
    tp_assigned = PaymentPlanFactory(
        name="Assigned TP",
        business_area=business_area,
        program_cycle=cycle,
        status=PaymentPlan.Status.FINISHED,
        created_by=user,
        total_households_count=777,
    )
    list_url = reverse(
        "api:payments:target-populations-list",
        kwargs={
            "business_area_slug": business_area.slug,
            "program_slug": program_active.slug,
        },
    )
    client = api_client(user)
    create_user_role_with_permissions(
        user,
        [Permissions.TARGETING_VIEW_LIST],
        business_area,
        program_active,
    )
    return {
        "business_area": business_area,
        "partner": partner,
        "user": user,
        "client": client,
        "program_active": program_active,
        "cycle": cycle,
        "tp": tp,
        "tp_locked": tp_locked,
        "tp_assigned": tp_assigned,
        "list_url": list_url,
    }


@pytest.fixture
def target_population_create_update_context(
    api_client: Callable,
    business_area: Any,
) -> dict[str, Any]:
    partner = PartnerFactory(name="unittest")
    user = UserFactory(partner=partner)
    program_active = ProgramFactory(business_area=business_area, status=Program.ACTIVE)
    cycle = ProgramCycleFactory(program=program_active, title="Cycle TP Create")

    tp = PaymentPlanFactory(
        business_area=business_area,
        program_cycle=cycle,
        status=PaymentPlan.Status.TP_OPEN,
        created_by=user,
    )
    create_url = reverse(
        "api:payments:target-populations-list",
        kwargs={
            "business_area_slug": business_area.slug,
            "program_slug": program_active.slug,
        },
    )
    update_url = reverse(
        "api:payments:target-populations-detail",
        kwargs={
            "business_area_slug": business_area.slug,
            "program_slug": program_active.slug,
            "pk": tp.pk,
        },
    )
    rules = [
        {
            "individua_ids": "",
            "household_ids": "",
            "households_filters_blocks": [
                {
                    "comparison_method": "RANGE",
                    "arguments": [1, 11],
                    "field_name": "size",
                    "flex_field_classification": "NOT_FLEX_FIELD",
                }
            ],
            "individuals_filters_blocks": [],
        }
    ]
    client = api_client(user)
    return {
        "business_area": business_area,
        "partner": partner,
        "user": user,
        "client": client,
        "program_active": program_active,
        "cycle": cycle,
        "tp": tp,
        "create_url": create_url,
        "update_url": update_url,
        "rules": rules,
    }


@pytest.fixture
def target_population_actions_context(
    api_client: Callable,
    business_area: Any,
) -> dict[str, Any]:
    partner = PartnerFactory(name="unittest")
    user = UserFactory(partner=partner)
    program_active = ProgramFactory(business_area=business_area, status=Program.ACTIVE)
    cycle = ProgramCycleFactory(program=program_active, title="Cycle TP Actions")

    client = api_client(user)
    target_population = PaymentPlanFactory(
        name="TP_OPEN",
        business_area=business_area,
        program_cycle=cycle,
        status=PaymentPlan.Status.TP_OPEN,
        created_by=user,
        created_at=timezone.datetime(2022, 2, 24, tzinfo=dt_timezone.utc),
    )
    url_kwargs = {
        "business_area_slug": business_area.slug,
        "program_slug": program_active.slug,
        "pk": target_population.pk,
    }
    return {
        "business_area": business_area,
        "partner": partner,
        "user": user,
        "client": client,
        "program_active": program_active,
        "cycle": cycle,
        "target_population": target_population,
        "url_lock": reverse("api:payments:target-populations-lock", kwargs=url_kwargs),
        "url_unlock": reverse("api:payments:target-populations-unlock", kwargs=url_kwargs),
        "url_rebuild": reverse("api:payments:target-populations-rebuild", kwargs=url_kwargs),
        "url_mark_ready": reverse("api:payments:target-populations-mark-ready", kwargs=url_kwargs),
        "url_copy": reverse("api:payments:target-populations-copy", kwargs=url_kwargs),
        "url_apply_steficon": reverse("api:payments:target-populations-apply-engine-formula", kwargs=url_kwargs),
    }


@pytest.fixture
def pending_payments_context(
    api_client: Callable,
    business_area: Any,
) -> dict[str, Any]:
    program = ProgramFactory(business_area=business_area, status=Program.ACTIVE)
    cycle = ProgramCycleFactory(program=program, title="Cycle Pending")

    partner = PartnerFactory(name="TestPartner")
    user = UserFactory(partner=partner)
    client = api_client(user)

    target_population = PaymentPlanFactory(
        name="TP_OPEN",
        business_area=business_area,
        program_cycle=cycle,
        status=PaymentPlan.Status.TP_OPEN,
        created_by=user,
        created_at=timezone.datetime(2022, 2, 24, tzinfo=dt_timezone.utc),
    )

    household1 = HouseholdFactory(program=program, business_area=business_area, size=3)
    PaymentFactory(
        household=household1,
        parent=target_population,
        collector=household1.head_of_household,
        head_of_household=household1.head_of_household,
        vulnerability_score=50.0,
        status_date=timezone.datetime(2022, 2, 24, tzinfo=dt_timezone.utc),
    )

    household2 = HouseholdFactory(
        program=program,
        business_area=business_area,
        unicef_id="HH-AAA-001",
        size=2,
    )
    household2.head_of_household.full_name = "Alice Smith"
    household2.head_of_household.save(update_fields=["full_name"])
    PaymentFactory(
        household=household2,
        parent=target_population,
        collector=household2.head_of_household,
        head_of_household=household2.head_of_household,
        vulnerability_score=15.5,
        status_date=timezone.datetime(2022, 2, 24, tzinfo=dt_timezone.utc),
    )

    household3 = HouseholdFactory(
        program=program,
        business_area=business_area,
        unicef_id="HH-ZZZ-001",
        size=5,
    )
    household3.head_of_household.full_name = "Zack Brown"
    household3.head_of_household.save(update_fields=["full_name"])
    PaymentFactory(
        household=household3,
        parent=target_population,
        collector=household3.head_of_household,
        head_of_household=household3.head_of_household,
        vulnerability_score=85.2,
        status_date=timezone.datetime(2022, 2, 24, tzinfo=dt_timezone.utc),
    )

    pending_payments_url = reverse(
        "api:payments:target-populations-pending-payments",
        kwargs={
            "business_area_slug": business_area.slug,
            "program_slug": program.slug,
            "pk": str(target_population.id),
        },
    )
    pending_payments_count_url = reverse(
        "api:payments:target-populations-pending-payments-count",
        kwargs={
            "business_area_slug": business_area.slug,
            "program_slug": program.slug,
            "pk": str(target_population.id),
        },
    )

    return {
        "business_area": business_area,
        "program": program,
        "user": user,
        "client": client,
        "target_population": target_population,
        "pending_payments_url": pending_payments_url,
        "pending_payments_count_url": pending_payments_count_url,
    }


def test_target_population_list_without_permissions(
    target_population_list_context: dict[str, Any],
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        target_population_list_context["user"],
        [Permissions.PM_ACCEPTANCE_PROCESS_APPROVE],
        target_population_list_context["business_area"],
        target_population_list_context["program_active"],
    )
    response = target_population_list_context["client"].get(target_population_list_context["tp_list_url"])
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.parametrize(
    "permissions",
    [
        [Permissions.TARGETING_VIEW_LIST],
    ],
)
def test_target_population_list_with_permissions(
    target_population_list_context: dict[str, Any],
    permissions: list,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        target_population_list_context["user"],
        permissions,
        target_population_list_context["business_area"],
        target_population_list_context["program_active"],
    )
    response = target_population_list_context["client"].get(target_population_list_context["tp_list_url"])
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()["results"]
    assert len(response_data) == 2

    response_count = target_population_list_context["client"].get(target_population_list_context["tp_count_url"])
    assert response_count.status_code == status.HTTP_200_OK
    assert response_count.json()["count"] == 2

    target_population_list_context["tp"].refresh_from_db()
    tp = response_data[1]
    assert str(target_population_list_context["tp"].id) == tp["id"]
    assert tp["name"] == "Test new TP"
    assert tp["status"] == target_population_list_context["tp"].get_status_display().upper()
    assert tp["total_households_count"] == target_population_list_context["tp"].total_households_count
    assert tp["total_individuals_count"] == target_population_list_context["tp"].total_individuals_count
    assert tp["created_at"] == target_population_list_context["tp"].created_at.strftime("%Y-%m-%dT%H:%M:%SZ")
    assert tp["updated_at"] == target_population_list_context["tp"].updated_at.strftime("%Y-%m-%dT%H:%M:%SZ")
    assert tp["created_by"] == target_population_list_context["user"].get_full_name()


def test_target_population_caching(
    target_population_list_context: dict[str, Any],
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        target_population_list_context["user"],
        [Permissions.TARGETING_VIEW_LIST],
        target_population_list_context["business_area"],
        target_population_list_context["program_active"],
    )
    with CaptureQueriesContext(connection) as ctx:
        response = target_population_list_context["client"].get(target_population_list_context["tp_list_url"])
        assert response.status_code == status.HTTP_200_OK

        etag = response.headers["etag"]
        assert json.loads(cache.get(etag)[0].decode("utf8")) == response.json()
        assert len(ctx.captured_queries) == 17

    with CaptureQueriesContext(connection) as ctx:
        response = target_population_list_context["client"].get(target_population_list_context["tp_list_url"])
        assert response.status_code == status.HTTP_200_OK

        etag_second_call = response.headers["etag"]
        assert json.loads(cache.get(response.headers["etag"])[0].decode("utf8")) == response.json()
        assert len(ctx.captured_queries) == 7
        assert etag_second_call == etag

    target_population_list_context["tp"].status = PaymentPlan.Status.TP_PROCESSING
    target_population_list_context["tp"].save()
    with CaptureQueriesContext(connection) as ctx:
        response = target_population_list_context["client"].get(target_population_list_context["tp_list_url"])
        assert response.status_code == status.HTTP_200_OK

        etag_call_after_update = response.headers["etag"]
        assert json.loads(cache.get(response.headers["etag"])[0].decode("utf8")) == response.json()
        assert len(ctx.captured_queries) == 11

        assert etag_call_after_update != etag

    with CaptureQueriesContext(connection) as ctx:
        response = target_population_list_context["client"].get(target_population_list_context["tp_list_url"])
        assert response.status_code == status.HTTP_200_OK

        etag_call_after_update_second_call = response.headers["etag"]
        assert json.loads(cache.get(response.headers["etag"])[0].decode("utf8")) == response.json()
        assert len(ctx.captured_queries) == 7
        assert etag_call_after_update_second_call == etag_call_after_update


@pytest.mark.parametrize(
    ("permissions", "expected_status"),
    [
        ([Permissions.TARGETING_VIEW_DETAILS], status.HTTP_200_OK),
        ([], status.HTTP_403_FORBIDDEN),
    ],
)
def test_target_population_detail_permissions(
    target_population_detail_context: dict[str, Any],
    permissions: list,
    expected_status: int,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        target_population_detail_context["user"],
        permissions,
        target_population_detail_context["business_area"],
        target_population_detail_context["program_active"],
    )

    response = target_population_detail_context["client"].get(target_population_detail_context["tp_detail_url"])
    assert response.status_code == expected_status


def test_target_population_detail(
    target_population_detail_context: dict[str, Any],
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        target_population_detail_context["user"],
        [Permissions.TARGETING_VIEW_DETAILS],
        target_population_detail_context["business_area"],
        target_population_detail_context["program_active"],
    )
    response = target_population_detail_context["client"].get(target_population_detail_context["tp_detail_url"])
    assert response.status_code == status.HTTP_200_OK

    tp = response.json()
    target_population_detail_context["tp"].refresh_from_db()

    assert tp["id"] == str(target_population_detail_context["tp"].id)
    assert tp["name"] == "TP Detail"
    assert tp["program_cycle"]["title"] == target_population_detail_context["cycle"].title
    assert tp["program"]["name"] == target_population_detail_context["program_active"].name
    assert tp["status"] == target_population_detail_context["tp"].status
    assert tp["total_households_count"] == target_population_detail_context["tp"].total_households_count
    assert tp["total_individuals_count"] == target_population_detail_context["tp"].total_individuals_count
    assert tp["created_by"] == (
        f"{target_population_detail_context['user'].first_name} {target_population_detail_context['user'].last_name}"
    )
    assert tp["background_action_status"] is None
    assert tp["male_children_count"] == target_population_detail_context["tp"].male_children_count
    assert tp["female_children_count"] == target_population_detail_context["tp"].female_children_count
    assert tp["male_adults_count"] == target_population_detail_context["tp"].male_adults_count
    assert tp["female_adults_count"] == target_population_detail_context["tp"].female_adults_count


def test_filter_by_status(target_population_filter_context: dict[str, Any]) -> None:
    response = target_population_filter_context["client"].get(
        target_population_filter_context["list_url"],
        {"status": PaymentPlan.Status.TP_LOCKED.value},
    )
    target_population_filter_context["tp_locked"].refresh_from_db()
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()["results"]
    assert len(response_data) == 1
    assert response_data[0]["id"] == str(target_population_filter_context["tp_locked"].id)
    assert response_data[0]["status"] == "LOCKED"
    assert response_data[0]["name"] == "LOCKED"

    response = target_population_filter_context["client"].get(
        target_population_filter_context["list_url"],
        {"status": "ASSIGNED"},
    )
    target_population_filter_context["tp_assigned"].refresh_from_db()
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()["results"]
    assert len(response_data) == 1
    assert response_data[0]["id"] == str(target_population_filter_context["tp_assigned"].id)
    assert response_data[0]["name"] == "Assigned TP"


def test_filter_by_program_cycle(
    target_population_filter_context: dict[str, Any],
) -> None:
    new_cycle = ProgramCycleFactory(program=target_population_filter_context["program_active"], title="Cycle QWOOL")

    new_tp = PaymentPlanFactory(
        name="TEST_ABC_QWOOL",
        business_area=target_population_filter_context["business_area"],
        program_cycle=new_cycle,
        status=PaymentPlan.Status.TP_STEFICON_RUN,
        created_by=target_population_filter_context["user"],
    )
    response = target_population_filter_context["client"].get(
        target_population_filter_context["list_url"],
        {"program_cycle": new_tp.program_cycle.id},
    )
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()["results"]
    assert len(response_data) == 1
    assert response_data[0]["name"] == "TEST_ABC_QWOOL"
    assert response_data[0]["status"] == "STEFICON RUN"


def test_filter_by_number_of_hh(target_population_filter_context: dict[str, Any]) -> None:
    PaymentPlanFactory(
        name="PP_1",
        business_area=target_population_filter_context["business_area"],
        program_cycle=target_population_filter_context["cycle"],
        status=PaymentPlan.Status.TP_LOCKED,
        created_by=target_population_filter_context["user"],
        total_households_count=100,
    )
    PaymentPlanFactory(
        name="PP_2",
        business_area=target_population_filter_context["business_area"],
        program_cycle=target_population_filter_context["cycle"],
        status=PaymentPlan.Status.TP_LOCKED,
        created_by=target_population_filter_context["user"],
        total_households_count=200,
    )
    response = target_population_filter_context["client"].get(
        target_population_filter_context["list_url"],
        {"total_households_count__gte": "99", "total_households_count__lte": 201},
    )
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()["results"]
    assert len(response_data) == 2
    assert response_data[0]["name"] == "PP_2"
    assert response_data[1]["name"] == "PP_1"

    response = target_population_filter_context["client"].get(
        target_population_filter_context["list_url"],
        {"total_households_count__lte": 101},
    )
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()["results"]
    assert len(response_data) == 1
    assert response_data[0]["name"] == "PP_1"


def test_filter_by_created_date(target_population_filter_context: dict[str, Any]) -> None:
    tp_1 = PaymentPlanFactory(
        name="TP_Mmmmmmm",
        business_area=target_population_filter_context["business_area"],
        program_cycle=target_population_filter_context["cycle"],
        status=PaymentPlan.Status.LOCKED_FSP,
        created_by=target_population_filter_context["user"],
    )
    tp_1.created_at = timezone.datetime(2022, 2, 24, tzinfo=dt_timezone.utc)
    tp_1.save(update_fields=["created_at"])
    tp_2 = PaymentPlanFactory(
        name="TP_Uuuuu_Aaaaa",
        business_area=target_population_filter_context["business_area"],
        program_cycle=target_population_filter_context["cycle"],
        status=PaymentPlan.Status.LOCKED_FSP,
        created_by=target_population_filter_context["user"],
    )
    tp_2.created_at = timezone.datetime(2022, 1, 1, tzinfo=dt_timezone.utc)
    tp_2.save(update_fields=["created_at"])
    response = target_population_filter_context["client"].get(
        target_population_filter_context["list_url"],
        {"created_at__gte": "2022-02-23", "created_at__lte": "2022-03-04"},
    )
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()["results"]
    assert len(response_data) == 1
    assert response_data[0]["name"] == tp_1.name

    response = target_population_filter_context["client"].get(
        target_population_filter_context["list_url"],
        {"created_at__lte": "2022-01-18"},
    )
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()["results"]
    assert len(response_data) == 1
    assert response_data[0]["name"] == tp_2.name


@pytest.mark.parametrize(
    ("permissions", "expected_status"),
    [
        ([Permissions.TARGETING_CREATE], status.HTTP_201_CREATED),
        ([], status.HTTP_403_FORBIDDEN),
    ],
)
def test_create_payment_plan_success(
    target_population_create_update_context: dict[str, Any],
    permissions: list,
    expected_status: int,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        target_population_create_update_context["user"],
        permissions,
        target_population_create_update_context["business_area"],
        target_population_create_update_context["program_active"],
    )
    data = {
        "name": "New Payment Plan",
        "program_cycle_id": target_population_create_update_context["cycle"].id,
        "rules": target_population_create_update_context["rules"],
        "excluded_ids": "IND-123",
        "exclusion_reason": "Just MMM Qwool Test",
        "flag_exclude_if_on_sanction_list": True,
        "flag_exclude_if_active_adjudication_ticket": False,
    }

    response = target_population_create_update_context["client"].post(
        target_population_create_update_context["create_url"],
        data,
        format="json",
    )
    assert response.status_code == expected_status
    if response.status_code == status.HTTP_201_CREATED:
        assert response.data["name"] == data["name"]
        assert response.data["rules"][0]["households_filters_blocks"][0]["field_name"] == "size"
        assert response.data["exclusion_reason"] == data["exclusion_reason"]
        assert response.data["excluded_ids"] == data["excluded_ids"]
        assert response.data["flag_exclude_if_on_sanction_list"] is True
        assert response.data["flag_exclude_if_active_adjudication_ticket"] is False


def test_create_payment_plan_invalid_data(
    target_population_create_update_context: dict[str, Any],
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        target_population_create_update_context["user"],
        [Permissions.TARGETING_CREATE],
        target_population_create_update_context["business_area"],
        target_population_create_update_context["program_active"],
    )
    invalid_data = {
        "name": "",
        "program_cycle_id": None,
        "rules": [],
    }
    response = target_population_create_update_context["client"].post(
        target_population_create_update_context["create_url"],
        invalid_data,
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "name" in response.data
    assert "program_cycle_id" in response.data


@pytest.mark.parametrize(
    ("permissions", "expected_status"),
    [
        ([Permissions.TARGETING_UPDATE], status.HTTP_200_OK),
        ([], status.HTTP_403_FORBIDDEN),
    ],
)
def test_update_payment_plan_success(
    target_population_create_update_context: dict[str, Any],
    permissions: list,
    expected_status: int,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        target_population_create_update_context["user"],
        permissions,
        target_population_create_update_context["business_area"],
        target_population_create_update_context["program_active"],
    )

    update_data = {
        "name": "Test with NEW NAME",
        "excluded_ids": "IND-999",
        "exclusion_reason": "123",
        "version": target_population_create_update_context["tp"].version,
    }

    response = target_population_create_update_context["client"].patch(
        target_population_create_update_context["update_url"],
        update_data,
        format="json",
    )

    assert response.status_code == expected_status
    if response.status_code == status.HTTP_200_OK:
        assert response.data["name"] == update_data["name"]
        assert response.data["exclusion_reason"] == update_data["exclusion_reason"]
        assert response.data["excluded_ids"] == update_data["excluded_ids"]


def test_update_payment_plan_invalid_data(
    target_population_create_update_context: dict[str, Any],
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        target_population_create_update_context["user"],
        [Permissions.TARGETING_UPDATE],
        target_population_create_update_context["business_area"],
        target_population_create_update_context["program_active"],
    )
    invalid_update_data = {
        "name": "",
        "version": target_population_create_update_context["tp"].version,
    }
    response = target_population_create_update_context["client"].patch(
        target_population_create_update_context["update_url"],
        invalid_update_data,
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "name" in response.data


@pytest.mark.parametrize(
    ("permissions", "expected_status"),
    [
        ([Permissions.TARGETING_LOCK], status.HTTP_200_OK),
        ([], status.HTTP_403_FORBIDDEN),
    ],
)
def test_lock(
    target_population_actions_context: dict[str, Any],
    permissions: list,
    expected_status: int,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        target_population_actions_context["user"],
        permissions,
        target_population_actions_context["business_area"],
        target_population_actions_context["program_active"],
    )

    response = target_population_actions_context["client"].get(target_population_actions_context["url_lock"])

    assert response.status_code == expected_status
    if expected_status == status.HTTP_200_OK:
        assert response.json() == {"message": "Target Population locked"}


@pytest.mark.parametrize(
    ("permissions", "expected_status"),
    [
        ([Permissions.TARGETING_UNLOCK], status.HTTP_200_OK),
        ([], status.HTTP_403_FORBIDDEN),
    ],
)
def test_unlock(
    target_population_actions_context: dict[str, Any],
    permissions: list,
    expected_status: int,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        target_population_actions_context["user"],
        permissions,
        target_population_actions_context["business_area"],
        target_population_actions_context["program_active"],
    )
    target_population_actions_context["target_population"].status = PaymentPlan.Status.TP_LOCKED
    target_population_actions_context["target_population"].save()

    response = target_population_actions_context["client"].get(target_population_actions_context["url_unlock"])
    assert response.status_code == expected_status
    if expected_status == status.HTTP_200_OK:
        assert response.json() == {"message": "Target Population unlocked"}


@pytest.mark.parametrize(
    ("permissions", "expected_status"),
    [
        ([Permissions.TARGETING_LOCK], status.HTTP_200_OK),
        ([], status.HTTP_403_FORBIDDEN),
    ],
)
def test_rebuild(
    target_population_actions_context: dict[str, Any],
    permissions: list,
    expected_status: int,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        target_population_actions_context["user"],
        permissions,
        target_population_actions_context["business_area"],
        target_population_actions_context["program_active"],
    )

    response = target_population_actions_context["client"].get(target_population_actions_context["url_rebuild"])

    assert response.status_code == expected_status
    if expected_status == status.HTTP_200_OK:
        assert response.json() == {"message": "Target Population rebuilding"}


@pytest.mark.parametrize(
    ("permissions", "expected_status"),
    [
        ([Permissions.TARGETING_CREATE, Permissions.TARGETING_SEND], status.HTTP_200_OK),
        ([], status.HTTP_403_FORBIDDEN),
    ],
)
def test_mark_ready(
    target_population_actions_context: dict[str, Any],
    permissions: list,
    expected_status: int,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        target_population_actions_context["user"],
        permissions,
        target_population_actions_context["business_area"],
        target_population_actions_context["program_active"],
    )
    target_population_actions_context[
        "target_population"
    ].financial_service_provider = FinancialServiceProviderFactory()
    target_population_actions_context["target_population"].delivery_mechanism = DeliveryMechanismFactory()
    target_population_actions_context["target_population"].status = PaymentPlan.Status.TP_LOCKED
    target_population_actions_context["target_population"].save()

    response = target_population_actions_context["client"].get(target_population_actions_context["url_mark_ready"])
    assert response.status_code == expected_status
    if expected_status == status.HTTP_200_OK:
        assert response.json() == {"message": "Target Population ready for Payment Plan"}


@pytest.mark.parametrize(
    ("permissions", "expected_status"),
    [
        ([Permissions.TARGETING_DUPLICATE], status.HTTP_201_CREATED),
        ([], status.HTTP_403_FORBIDDEN),
    ],
)
def test_copy_tp(
    target_population_actions_context: dict[str, Any],
    permissions: list,
    expected_status: int,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        target_population_actions_context["user"],
        permissions,
        target_population_actions_context["business_area"],
        target_population_actions_context["program_active"],
    )
    data = {"name": "Copied TP test 123", "program_cycle_id": target_population_actions_context["cycle"].pk}
    response = target_population_actions_context["client"].post(
        target_population_actions_context["url_copy"],
        data,
        format="json",
    )

    assert response.status_code == expected_status
    if expected_status == status.HTTP_201_CREATED:
        assert "id" in response.json()
        assert PaymentPlan.objects.filter(name="Copied TP test 123").count() == 1
        assert PaymentPlan.objects.all().count() == 2


def test_copy_tp_validation_errors(
    target_population_actions_context: dict[str, Any],
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        target_population_actions_context["user"],
        [Permissions.TARGETING_DUPLICATE],
        target_population_actions_context["business_area"],
        target_population_actions_context["program_active"],
    )
    cycle = ProgramCycleFactory(program=target_population_actions_context["program_active"], title="Cycle123")

    PaymentPlanFactory(
        name="Copied TP AGAIN",
        business_area=target_population_actions_context["business_area"],
        program_cycle=cycle,
    )
    data = {
        "name": "Copied TP AGAIN",
        "program_cycle_id": cycle.pk,
    }
    response = target_population_actions_context["client"].post(
        target_population_actions_context["url_copy"],
        data,
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Target Population with name: Copied TP AGAIN and program cycle: Cycle123 already exists." in response.data

    cycle.status = ProgramCycle.FINISHED
    cycle.save()
    response_2 = target_population_actions_context["client"].post(
        target_population_actions_context["url_copy"],
        data,
        format="json",
    )

    assert response_2.status_code == status.HTTP_400_BAD_REQUEST
    assert "Not possible to assign Finished Program Cycle to Targeting." in response_2.data

    response_3 = target_population_actions_context["client"].post(
        target_population_actions_context["url_copy"],
        {},
        format="json",
    )
    assert response_3.status_code == status.HTTP_400_BAD_REQUEST
    assert "name" in response_3.data
    assert "program_cycle_id" in response_3.data


@pytest.mark.parametrize(
    ("permissions", "expected_status"),
    [
        ([Permissions.TARGETING_UPDATE], status.HTTP_200_OK),
        ([], status.HTTP_403_FORBIDDEN),
    ],
)
def test_apply_engine_formula_tp(
    target_population_actions_context: dict[str, Any],
    permissions: list,
    expected_status: int,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        target_population_actions_context["user"],
        permissions,
        target_population_actions_context["business_area"],
        target_population_actions_context["program_active"],
    )
    rule_for_tp = RuleCommitFactory(
        rule__type=Rule.TYPE_TARGETING,
        rule__enabled=True,
        version=11,
        is_release=True,
    ).rule
    target_population_actions_context["target_population"].status = PaymentPlan.Status.TP_LOCKED
    target_population_actions_context["target_population"].save()
    data = {
        "engine_formula_rule_id": str(rule_for_tp.pk),
        "version": target_population_actions_context["target_population"].version,
    }
    response = target_population_actions_context["client"].post(
        target_population_actions_context["url_apply_steficon"],
        data,
        format="json",
    )

    assert response.status_code == expected_status
    if expected_status == status.HTTP_200_OK:
        resp_data = response.json()
        assert "id" in resp_data
        assert "TARGETING" in resp_data["steficon_rule_targeting"]["rule"]["type"]
        assert "STEFICON_WAIT" in resp_data["status"]


def test_apply_engine_formula_tp_validation_errors(
    target_population_actions_context: dict[str, Any],
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        target_population_actions_context["user"],
        [Permissions.TARGETING_UPDATE],
        target_population_actions_context["business_area"],
        target_population_actions_context["program_active"],
    )
    rule_for_tp = RuleCommitFactory(rule__type=Rule.TYPE_TARGETING, rule__enabled=False, version=22).rule
    target_population_actions_context["target_population"].status = PaymentPlan.Status.TP_STEFICON_ERROR
    target_population_actions_context["target_population"].save()

    data = {
        "engine_formula_rule_id": rule_for_tp.pk,
        "version": target_population_actions_context["target_population"].version,
    }
    response = target_population_actions_context["client"].post(
        target_population_actions_context["url_apply_steficon"],
        data,
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "This engine rule is not enabled or is deprecated." in response.data

    target_population_actions_context["target_population"].status = PaymentPlan.Status.TP_OPEN
    target_population_actions_context["target_population"].save()
    data = {
        "engine_formula_rule_id": rule_for_tp.pk,
        "version": target_population_actions_context["target_population"].version,
    }
    response_2 = target_population_actions_context["client"].post(
        target_population_actions_context["url_apply_steficon"],
        data,
        format="json",
    )

    assert response_2.status_code == status.HTTP_400_BAD_REQUEST
    assert "Not allowed to run engine formula within status TP_OPEN." in response_2.data

    response_3 = target_population_actions_context["client"].post(
        target_population_actions_context["url_apply_steficon"],
        {},
        format="json",
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "engine_formula_rule_id" in response_3.data


@pytest.mark.parametrize(
    ("permissions", "expected_status"),
    [
        ([Permissions.TARGETING_REMOVE], status.HTTP_204_NO_CONTENT),
        ([], status.HTTP_403_FORBIDDEN),
    ],
)
def test_tp_delete(
    target_population_actions_context: dict[str, Any],
    permissions: list,
    expected_status: int,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        target_population_actions_context["user"],
        permissions,
        target_population_actions_context["business_area"],
        target_population_actions_context["program_active"],
    )
    tp = PaymentPlanFactory(
        name="TP_to_delete",
        business_area=target_population_actions_context["business_area"],
        program_cycle=target_population_actions_context["cycle"],
        status=PaymentPlan.Status.TP_OPEN,
        created_by=target_population_actions_context["user"],
    )
    delete_url = reverse(
        "api:payments:target-populations-detail",
        kwargs={
            "business_area_slug": target_population_actions_context["business_area"].slug,
            "program_slug": target_population_actions_context["program_active"].slug,
            "pk": tp.pk,
        },
    )
    response = target_population_actions_context["client"].delete(delete_url)

    assert response.status_code == expected_status
    if expected_status == status.HTTP_204_NO_CONTENT:
        assert PaymentPlan.objects.filter(name="TP_to_delete").count() == 0
        assert PaymentPlan.all_objects.filter(name="TP_to_delete").count() == 1


def test_vulnerability_score_filter_applies_correctly(
    target_population_actions_context: dict[str, Any],
    create_user_role_with_permissions: Any,
    django_capture_on_commit_callbacks: Any,
) -> None:
    create_user_role_with_permissions(
        target_population_actions_context["user"],
        [Permissions.TARGETING_UPDATE, Permissions.TARGETING_LOCK],
        target_population_actions_context["business_area"],
        target_population_actions_context["program_active"],
    )

    household1 = HouseholdFactory(
        program=target_population_actions_context["program_active"],
        business_area=target_population_actions_context["business_area"],
        size=2,
    )
    household2 = HouseholdFactory(
        program=target_population_actions_context["program_active"],
        business_area=target_population_actions_context["business_area"],
        size=2,
    )
    household3 = HouseholdFactory(
        program=target_population_actions_context["program_active"],
        business_area=target_population_actions_context["business_area"],
        size=2,
    )

    PaymentFactory(
        parent=target_population_actions_context["target_population"],
        household=household1,
        head_of_household=household1.head_of_household,
        collector=household1.head_of_household,
    )
    PaymentFactory(
        parent=target_population_actions_context["target_population"],
        household=household2,
        head_of_household=household2.head_of_household,
        collector=household2.head_of_household,
    )
    PaymentFactory(
        parent=target_population_actions_context["target_population"],
        household=household3,
        head_of_household=household3.head_of_household,
        collector=household3.head_of_household,
    )

    target_population_actions_context["target_population"].status = PaymentPlan.Status.TP_LOCKED
    steficon_rule_commit = RuleCommitFactory(
        rule__type=Rule.TYPE_TARGETING, rule__enabled=True, enabled=True, is_release=True
    )
    target_population_actions_context["target_population"].save()
    target_population_actions_context["target_population"].refresh_from_db()

    apply_formula_url = reverse(
        "api:payments:target-populations-apply-engine-formula",
        kwargs={
            "business_area_slug": target_population_actions_context["business_area"].slug,
            "program_slug": target_population_actions_context["program_active"].slug,
            "pk": target_population_actions_context["target_population"].pk,
        },
    )

    values = {
        household1.id: 25.0,
        household2.id: 50.0,
        household3.id: 75.0,
    }

    with patch(
        "hope.models.rule.RuleCommit.execute",
        autospec=True,
        side_effect=lambda _self, context, _values=values: MagicMock(value=_values[context["household"].id]),
    ):
        apply_formula_data = {
            "engine_formula_rule_id": str(steficon_rule_commit.rule.pk),
            "version": target_population_actions_context["target_population"].version,
        }
        with django_capture_on_commit_callbacks(execute=True):
            response = target_population_actions_context["client"].post(
                apply_formula_url,
                apply_formula_data,
                format="json",
            )
            assert response.status_code == status.HTTP_200_OK

    target_population_actions_context["target_population"].refresh_from_db()
    assert target_population_actions_context["target_population"].status == PaymentPlan.Status.TP_STEFICON_COMPLETED

    assert target_population_actions_context["target_population"].payment_items.count() == 3
    payment1 = target_population_actions_context["target_population"].payment_items.get(household=household1)
    payment2 = target_population_actions_context["target_population"].payment_items.get(household=household2)
    payment3 = target_population_actions_context["target_population"].payment_items.get(household=household3)
    assert payment1.vulnerability_score == 25.0
    assert payment2.vulnerability_score == 50.0
    assert payment3.vulnerability_score == 75.0

    update_url = reverse(
        "api:payments:target-populations-detail",
        kwargs={
            "business_area_slug": target_population_actions_context["business_area"].slug,
            "program_slug": target_population_actions_context["program_active"].slug,
            "pk": target_population_actions_context["target_population"].pk,
        },
    )

    update_data = {
        "vulnerability_score_min": 30.00,
        "vulnerability_score_max": 70.00,
        "version": target_population_actions_context["target_population"].version,
    }
    with django_capture_on_commit_callbacks(execute=True):
        response = target_population_actions_context["client"].patch(
            update_url,
            update_data,
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK

    target_population_actions_context["target_population"].refresh_from_db()
    assert target_population_actions_context["target_population"].vulnerability_score_min == 30.0
    assert target_population_actions_context["target_population"].vulnerability_score_max == 70.0

    payment1.refresh_from_db()
    payment2.refresh_from_db()
    payment3.refresh_from_db()
    assert payment1.is_removed is True
    assert payment2.is_removed is False
    assert payment3.is_removed is True

    active_payments = target_population_actions_context["target_population"].payment_items.all()
    assert active_payments.count() == 1
    assert active_payments.first().household == household2


def test_vulnerability_score_filter_set_before_engine_formula(
    target_population_actions_context: dict[str, Any],
    create_user_role_with_permissions: Any,
    django_capture_on_commit_callbacks: Any,
) -> None:
    create_user_role_with_permissions(
        target_population_actions_context["user"],
        [Permissions.TARGETING_UPDATE, Permissions.TARGETING_LOCK],
        target_population_actions_context["business_area"],
        target_population_actions_context["program_active"],
    )

    household1 = HouseholdFactory(
        program=target_population_actions_context["program_active"],
        business_area=target_population_actions_context["business_area"],
        size=2,
    )
    household2 = HouseholdFactory(
        program=target_population_actions_context["program_active"],
        business_area=target_population_actions_context["business_area"],
        size=2,
    )
    household3 = HouseholdFactory(
        program=target_population_actions_context["program_active"],
        business_area=target_population_actions_context["business_area"],
        size=2,
    )

    PaymentFactory(
        parent=target_population_actions_context["target_population"],
        household=household1,
        head_of_household=household1.head_of_household,
        collector=household1.head_of_household,
    )
    PaymentFactory(
        parent=target_population_actions_context["target_population"],
        household=household2,
        head_of_household=household2.head_of_household,
        collector=household2.head_of_household,
    )
    PaymentFactory(
        parent=target_population_actions_context["target_population"],
        household=household3,
        head_of_household=household3.head_of_household,
        collector=household3.head_of_household,
    )

    target_population_actions_context["target_population"].status = PaymentPlan.Status.TP_LOCKED
    steficon_rule_commit = RuleCommitFactory(
        rule__type=Rule.TYPE_TARGETING, rule__enabled=True, enabled=True, is_release=True
    )
    target_population_actions_context["target_population"].save()
    target_population_actions_context["target_population"].refresh_from_db()

    update_url = reverse(
        "api:payments:target-populations-detail",
        kwargs={
            "business_area_slug": target_population_actions_context["business_area"].slug,
            "program_slug": target_population_actions_context["program_active"].slug,
            "pk": target_population_actions_context["target_population"].pk,
        },
    )

    update_data = {
        "vulnerability_score_min": 30.00,
        "vulnerability_score_max": 70.00,
        "version": target_population_actions_context["target_population"].version,
    }
    response = target_population_actions_context["client"].patch(
        update_url,
        update_data,
        format="json",
    )
    assert response.status_code == status.HTTP_200_OK

    target_population_actions_context["target_population"].refresh_from_db()
    assert target_population_actions_context["target_population"].vulnerability_score_min == 30.0
    assert target_population_actions_context["target_population"].vulnerability_score_max == 70.0

    payment1 = target_population_actions_context["target_population"].payment_items.get(household=household1)
    payment2 = target_population_actions_context["target_population"].payment_items.get(household=household2)
    payment3 = target_population_actions_context["target_population"].payment_items.get(household=household3)
    assert payment1.vulnerability_score is None
    assert payment2.vulnerability_score is None
    assert payment3.vulnerability_score is None
    assert payment1.is_removed is False
    assert payment2.is_removed is False
    assert payment3.is_removed is False

    apply_formula_url = reverse(
        "api:payments:target-populations-apply-engine-formula",
        kwargs={
            "business_area_slug": target_population_actions_context["business_area"].slug,
            "program_slug": target_population_actions_context["program_active"].slug,
            "pk": target_population_actions_context["target_population"].pk,
        },
    )

    values = {
        household1.id: 25.0,
        household2.id: 50.0,
        household3.id: 75.0,
    }

    with patch(
        "hope.models.rule.RuleCommit.execute",
        autospec=True,
        side_effect=lambda _self, context, _values=values: MagicMock(value=_values[context["household"].id]),
    ):
        apply_formula_data = {
            "engine_formula_rule_id": str(steficon_rule_commit.rule.pk),
            "version": target_population_actions_context["target_population"].version,
        }
        with django_capture_on_commit_callbacks(execute=True):
            response = target_population_actions_context["client"].post(
                apply_formula_url,
                apply_formula_data,
                format="json",
            )
            assert response.status_code == status.HTTP_200_OK

    target_population_actions_context["target_population"].refresh_from_db()
    assert target_population_actions_context["target_population"].status == PaymentPlan.Status.TP_STEFICON_COMPLETED

    payment1.refresh_from_db()
    payment2.refresh_from_db()
    payment3.refresh_from_db()

    assert payment1.vulnerability_score == 25.0
    assert payment2.vulnerability_score == 50.0
    assert payment3.vulnerability_score == 75.0

    assert payment1.is_removed is True
    assert payment2.is_removed is False
    assert payment3.is_removed is True

    active_payments = target_population_actions_context["target_population"].payment_items.all()
    assert active_payments.count() == 1
    assert active_payments.first().household == household2


@pytest.mark.parametrize(
    ("permissions", "expected_status"),
    [
        ([Permissions.TARGETING_VIEW_DETAILS], status.HTTP_200_OK),
        ([], status.HTTP_403_FORBIDDEN),
    ],
)
def test_pending_payments(
    pending_payments_context: dict[str, Any],
    permissions: list,
    expected_status: int,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        user=pending_payments_context["user"],
        permissions=permissions,
        business_area=pending_payments_context["business_area"],
        program=pending_payments_context["program"],
    )
    response = pending_payments_context["client"].get(pending_payments_context["pending_payments_url"])

    assert response.status_code == expected_status


def test_pending_payments_count(
    pending_payments_context: dict[str, Any],
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        user=pending_payments_context["user"],
        permissions=[Permissions.TARGETING_VIEW_DETAILS],
        business_area=pending_payments_context["business_area"],
        program=pending_payments_context["program"],
    )

    response = pending_payments_context["client"].get(pending_payments_context["pending_payments_count_url"])
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["count"] == 3


@pytest.mark.parametrize(
    ("ordering_param", "db_field"),
    [
        ("household_unicef_id", "household__unicef_id"),
        ("-household_unicef_id", "-household__unicef_id"),
        ("household_size", "household__size"),
        ("-household_size", "-household__size"),
        ("household_admin2", "household__admin2__name"),
        ("-household_admin2", "-household__admin2__name"),
        ("head_of_household", "head_of_household__full_name"),
        ("-head_of_household", "-head_of_household__full_name"),
        ("vulnerability_score", "vulnerability_score"),
        ("-vulnerability_score", "-vulnerability_score"),
    ],
)
def test_pending_payments_ordering(
    pending_payments_context: dict[str, Any],
    ordering_param: str,
    db_field: str,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        user=pending_payments_context["user"],
        permissions=[Permissions.TARGETING_VIEW_DETAILS],
        business_area=pending_payments_context["business_area"],
        program=pending_payments_context["program"],
    )

    response = pending_payments_context["client"].get(
        pending_payments_context["pending_payments_url"],
        {"ordering": ordering_param},
    )
    assert response.status_code == status.HTTP_200_OK

    results = response.json().get("results", [])
    returned_ids = [r["id"] for r in results]

    expected_ids_qs = list(
        Payment.objects.filter(parent=pending_payments_context["target_population"])
        .order_by(db_field)
        .values_list("id", flat=True)
    )
    expected_ids = [str(i) for i in expected_ids_qs]

    assert returned_ids == expected_ids
