from datetime import date
from decimal import Decimal
import json
from typing import Any, Callable

from django.core.cache import cache
from django.db import connection
from django.test.utils import CaptureQueriesContext
import pytest
from rest_framework import status
from rest_framework.reverse import reverse

from extras.test_utils.factories import (
    BusinessAreaFactory,
    CurrencyFactory,
    DeliveryMechanismFactory,
    FinancialServiceProviderFactory,
    FinancialServiceProviderXlsxTemplateFactory,
    FspXlsxTemplatePerDeliveryMechanismFactory,
    PartnerFactory,
    PaymentPlanFactory,
    PaymentPlanGroupFactory,
    PaymentPlanPurposeFactory,
    PaymentPlanSplitFactory,
    ProgramCycleFactory,
    ProgramFactory,
    UserFactory,
)
from hope.apps.account.permissions import Permissions
from hope.models import FinancialServiceProvider, PaymentPlan, Program

pytestmark = pytest.mark.django_db


@pytest.fixture
def business_area() -> Any:
    return BusinessAreaFactory(slug="afghanistan")


@pytest.fixture
def payment_plan_list_context(
    api_client: Callable,
    business_area: Any,
) -> dict[str, Any]:
    partner = PartnerFactory(name="unittest")
    user = UserFactory(partner=partner)
    program_active = ProgramFactory(business_area=business_area, status=Program.ACTIVE)
    cycle = ProgramCycleFactory(program=program_active)
    pp = PaymentPlanFactory(
        business_area=business_area,
        program_cycle=cycle,
        status=PaymentPlan.Status.IN_APPROVAL,
        created_by=user,
        name="PP List",
        currency=CurrencyFactory(code="USD", name="United States Dollar"),
        excluded_ids="HH-1",
        dispersion_start_date=date(2025, 2, 1),
        dispersion_end_date=date(2025, 3, 1),
        total_entitled_quantity=Decimal("100.00"),
        total_delivered_quantity=Decimal("40.00"),
        total_undelivered_quantity=Decimal("60.00"),
    )
    tp = PaymentPlanFactory(
        business_area=business_area,
        program_cycle=cycle,
        status=PaymentPlan.Status.TP_OPEN,
        created_by=user,
    )
    pp_list_url = reverse(
        "api:payments:payment-plans-list",
        kwargs={
            "business_area_slug": business_area.slug,
            "program_code": program_active.code,
        },
    )
    pp_count_url = reverse(
        "api:payments:payment-plans-count",
        kwargs={
            "business_area_slug": business_area.slug,
            "program_code": program_active.code,
        },
    )
    client = api_client(user)
    pp.unicef_id = "PP-LIST-0001"
    pp.save(update_fields=["unicef_id"])
    return {
        "business_area": business_area,
        "partner": partner,
        "user": user,
        "client": client,
        "program_active": program_active,
        "cycle": cycle,
        "pp": pp,
        "tp": tp,
        "pp_list_url": pp_list_url,
        "pp_count_url": pp_count_url,
    }


@pytest.fixture
def payment_plan_detail_context(
    api_client: Callable,
    business_area: Any,
) -> dict[str, Any]:
    partner = PartnerFactory(name="unittest")
    user = UserFactory(partner=partner)
    program_active = ProgramFactory(business_area=business_area, status=Program.ACTIVE)
    cycle = ProgramCycleFactory(program=program_active)
    pp = PaymentPlanFactory(
        business_area=business_area,
        program_cycle=cycle,
        status=PaymentPlan.Status.IN_APPROVAL,
        created_by=user,
        name="PP Detail",
        currency=CurrencyFactory(code="USD", name="United States Dollar"),
        excluded_ids="HH-1",
        dispersion_start_date=date(2025, 2, 1),
        dispersion_end_date=date(2025, 3, 1),
        total_entitled_quantity=Decimal("100.00"),
        total_delivered_quantity=Decimal("40.00"),
        total_undelivered_quantity=Decimal("60.00"),
    )
    pp_detail_url = reverse(
        "api:payments:payment-plans-detail",
        kwargs={
            "business_area_slug": business_area.slug,
            "program_code": program_active.code,
            "pk": str(pp.id),
        },
    )
    purpose = PaymentPlanPurposeFactory(business_area=business_area)
    pp.payment_plan_purposes.add(purpose)
    client = api_client(user)
    pp.unicef_id = "PP-DETAIL-0001"
    pp.save(update_fields=["unicef_id"])
    return {
        "business_area": business_area,
        "partner": partner,
        "user": user,
        "client": client,
        "program_active": program_active,
        "cycle": cycle,
        "pp": pp,
        "purpose": purpose,
        "group": pp.payment_plan_group,
        "pp_detail_url": pp_detail_url,
    }


@pytest.fixture
def payment_plan_filter_context(
    api_client: Callable,
    business_area: Any,
    create_user_role_with_permissions: Any,
) -> dict[str, Any]:
    partner = PartnerFactory(name="unittest")
    user = UserFactory(partner=partner)
    program_active = ProgramFactory(business_area=business_area, status=Program.ACTIVE)
    cycle = ProgramCycleFactory(program=program_active)
    pp = PaymentPlanFactory(
        business_area=business_area,
        program_cycle=cycle,
        status=PaymentPlan.Status.IN_APPROVAL,
        created_by=user,
        name="PP Filter Open",
    )
    pp_finished = PaymentPlanFactory(
        business_area=business_area,
        program_cycle=cycle,
        status=PaymentPlan.Status.FINISHED,
        created_by=user,
        name="PP Filter Finished",
    )
    list_url = reverse(
        "api:payments:payment-plans-list",
        kwargs={
            "business_area_slug": business_area.slug,
            "program_code": program_active.code,
        },
    )
    client = api_client(user)
    create_user_role_with_permissions(
        user,
        [Permissions.PM_VIEW_LIST],
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
        "pp": pp,
        "pp_finished": pp_finished,
        "list_url": list_url,
    }


def test_payment_plan_list_without_permissions(
    payment_plan_list_context: dict[str, Any],
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        payment_plan_list_context["user"],
        [Permissions.PM_ACCEPTANCE_PROCESS_APPROVE],
        payment_plan_list_context["business_area"],
        payment_plan_list_context["program_active"],
    )
    response = payment_plan_list_context["client"].get(payment_plan_list_context["pp_list_url"])
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.parametrize(
    "permissions",
    [
        [Permissions.PM_VIEW_LIST],
    ],
)
def test_payment_plan_list_with_permissions(
    payment_plan_list_context: dict[str, Any],
    permissions: list,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        payment_plan_list_context["user"],
        permissions,
        payment_plan_list_context["business_area"],
        payment_plan_list_context["program_active"],
    )
    response = payment_plan_list_context["client"].get(payment_plan_list_context["pp_list_url"])
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()["results"]
    assert len(response_data) == 1

    response_count = payment_plan_list_context["client"].get(payment_plan_list_context["pp_count_url"])
    assert response_count.status_code == status.HTTP_200_OK
    assert response_count.json()["count"] == 1

    payment_plan_list_context["pp"].refresh_from_db()
    payment_plan = response_data[0]
    assert str(payment_plan_list_context["pp"].id) == payment_plan["id"]
    assert payment_plan["unicef_id"] == "PP-LIST-0001"
    assert payment_plan["name"] == "PP List"
    assert payment_plan["status"] == payment_plan_list_context["pp"].status
    assert payment_plan["total_households_count"] == payment_plan_list_context["pp"].total_households_count
    assert payment_plan["currency"] == "USD"
    assert payment_plan["excluded_ids"] == "HH-1"
    assert payment_plan["total_entitled_quantity"] == "100.00"
    assert payment_plan["total_delivered_quantity"] == "40.00"
    assert payment_plan["total_undelivered_quantity"] == "60.00"
    assert payment_plan["dispersion_start_date"] == "2025-02-01"
    assert payment_plan["dispersion_end_date"] == "2025-03-01"
    assert payment_plan["plan_type"] == payment_plan_list_context["pp"].plan_type
    assert payment_plan["follow_ups"] == []
    assert payment_plan["top_ups"] == []


def test_payment_plan_caching(
    payment_plan_list_context: dict[str, Any],
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        payment_plan_list_context["user"],
        [Permissions.PM_VIEW_LIST],
        payment_plan_list_context["business_area"],
        payment_plan_list_context["program_active"],
    )
    with CaptureQueriesContext(connection) as ctx:
        response = payment_plan_list_context["client"].get(payment_plan_list_context["pp_list_url"])
        assert response.status_code == status.HTTP_200_OK
        assert response.has_header("etag")
        etag = response.headers["etag"]
        assert json.loads(cache.get(etag)[0].decode("utf8")) == response.json()
        assert len(response.json()["results"]) == 1
        assert len(ctx.captured_queries) == 18

    with CaptureQueriesContext(connection) as ctx:
        response = payment_plan_list_context["client"].get(payment_plan_list_context["pp_list_url"])
        assert response.status_code == status.HTTP_200_OK
        assert response.has_header("etag")
        etag_second_call = response.headers["etag"]
        assert etag == etag_second_call
        assert len(ctx.captured_queries) == 7

    payment_plan_list_context["pp"].status = PaymentPlan.Status.IN_REVIEW
    payment_plan_list_context["pp"].save()
    with CaptureQueriesContext(connection) as ctx:
        response = payment_plan_list_context["client"].get(payment_plan_list_context["pp_list_url"])
        assert response.status_code == status.HTTP_200_OK
        assert response.has_header("etag")
        new_etag = response.headers["etag"]
        assert json.loads(cache.get(new_etag)[0].decode("utf8")) == response.json()
        assert len(response.json()["results"]) == 1
        assert len(ctx.captured_queries) == 12

    with CaptureQueriesContext(connection) as ctx:
        response = payment_plan_list_context["client"].get(payment_plan_list_context["pp_list_url"])
        assert response.status_code == status.HTTP_200_OK
        assert response.has_header("etag")
        etag_second_call = response.headers["etag"]
        assert new_etag == etag_second_call
        assert len(ctx.captured_queries) == 7

    PaymentPlanFactory(
        business_area=payment_plan_list_context["business_area"],
        program_cycle=payment_plan_list_context["cycle"],
        status=PaymentPlan.Status.OPEN,
        created_by=payment_plan_list_context["user"],
    )
    with CaptureQueriesContext(connection) as ctx:
        response = payment_plan_list_context["client"].get(payment_plan_list_context["pp_list_url"])
        assert response.status_code == status.HTTP_200_OK
        assert response.has_header("etag")
        etag = response.headers["etag"]
        assert json.loads(cache.get(etag)[0].decode("utf8")) == response.json()
        assert len(response.json()["results"]) == 2
        assert len(ctx.captured_queries) == 14

    with CaptureQueriesContext(connection) as ctx:
        response = payment_plan_list_context["client"].get(payment_plan_list_context["pp_list_url"])
        assert response.status_code == status.HTTP_200_OK
        assert response.has_header("etag")
        etag_second_call = response.headers["etag"]
        assert etag == etag_second_call
        assert len(ctx.captured_queries) == 7

    payment_plan_list_context["pp"].delete()
    with CaptureQueriesContext(connection) as ctx:
        response = payment_plan_list_context["client"].get(payment_plan_list_context["pp_list_url"])
        assert response.status_code == status.HTTP_200_OK
        assert response.has_header("etag")
        etag = response.headers["etag"]
        assert json.loads(cache.get(etag)[0].decode("utf8")) == response.json()
        assert len(response.json()["results"]) == 1
        assert len(ctx.captured_queries) == 12

    with CaptureQueriesContext(connection) as ctx:
        response = payment_plan_list_context["client"].get(payment_plan_list_context["pp_list_url"])
        assert response.status_code == status.HTTP_200_OK
        assert response.has_header("etag")
        last_etag_second_call = response.headers["etag"]
        assert etag == last_etag_second_call
        assert len(ctx.captured_queries) == 7

    payment_plan_list_context["tp"].status = PaymentPlan.Status.TP_LOCKED
    payment_plan_list_context["tp"].save()
    with CaptureQueriesContext(connection) as ctx:
        response = payment_plan_list_context["client"].get(payment_plan_list_context["pp_list_url"])
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()["results"]) == 1
        assert response.has_header("etag")
        get_etag = response.headers["etag"]
        assert get_etag == last_etag_second_call
        assert len(ctx.captured_queries) == 7


@pytest.mark.parametrize(
    ("permissions", "expected_status"),
    [
        ([Permissions.PM_VIEW_DETAILS], status.HTTP_200_OK),
        ([], status.HTTP_403_FORBIDDEN),
    ],
)
def test_payment_plan_detail_permissions(
    payment_plan_detail_context: dict[str, Any],
    permissions: list,
    expected_status: int,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        payment_plan_detail_context["user"],
        permissions,
        payment_plan_detail_context["business_area"],
        payment_plan_detail_context["program_active"],
    )

    response = payment_plan_detail_context["client"].get(payment_plan_detail_context["pp_detail_url"])
    assert response.status_code == expected_status


def test_payment_plan_detail(
    payment_plan_detail_context: dict[str, Any],
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        payment_plan_detail_context["user"],
        [Permissions.PM_VIEW_DETAILS],
        payment_plan_detail_context["business_area"],
        payment_plan_detail_context["program_active"],
    )
    response = payment_plan_detail_context["client"].get(payment_plan_detail_context["pp_detail_url"])
    assert response.status_code == status.HTTP_200_OK

    payment_plan = response.json()
    payment_plan_detail_context["pp"].refresh_from_db()

    assert payment_plan["id"] == str(payment_plan_detail_context["pp"].id)
    assert payment_plan["unicef_id"] == "PP-DETAIL-0001"
    assert payment_plan["name"] == "PP Detail"
    assert payment_plan["status"] == payment_plan_detail_context["pp"].status
    assert payment_plan["total_households_count"] == payment_plan_detail_context["pp"].total_households_count
    assert payment_plan["currency"] == "USD"
    assert payment_plan["excluded_ids"] == "HH-1"
    assert payment_plan["total_entitled_quantity"] == "100.00"
    assert payment_plan["total_delivered_quantity"] == "40.00"
    assert payment_plan["total_undelivered_quantity"] == "60.00"
    assert payment_plan["dispersion_start_date"] == "2025-02-01"
    assert payment_plan["dispersion_end_date"] == "2025-03-01"
    assert payment_plan["plan_type"] == payment_plan_detail_context["pp"].plan_type
    assert payment_plan["follow_ups"] == []
    assert payment_plan["top_ups"] == []
    assert payment_plan["created_by"] == (
        f"{payment_plan_detail_context['user'].first_name} {payment_plan_detail_context['user'].last_name}"
    )
    assert payment_plan["background_action_status"] is None
    assert payment_plan["start_date"] is None
    assert payment_plan["program"]["name"] == payment_plan_detail_context["program_active"].name
    assert payment_plan["has_payment_list_export_file"] is False
    assert payment_plan["has_fsp_delivery_mechanism_xlsx_template"] is False
    assert payment_plan["imported_file_name"] == ""
    assert payment_plan["payments_conflicts_count"] == 0
    assert payment_plan["delivery_mechanism"] is None
    assert payment_plan["bank_reconciliation_success"] == 0
    assert payment_plan["bank_reconciliation_error"] == 0
    assert payment_plan["can_create_payment_verification_plan"] is False
    assert payment_plan["available_payment_records_count"] == 0
    assert payment_plan["can_create_follow_up"] is False
    assert payment_plan["total_withdrawn_households_count"] == 0
    assert payment_plan["unsuccessful_payments_count"] == 0
    assert payment_plan["can_send_to_payment_gateway"] is False
    assert payment_plan["can_split"] is False
    assert payment_plan["total_households_count_with_valid_phone_no"] == 0
    assert payment_plan["can_export_xlsx"] is False
    assert payment_plan["can_download_xlsx"] is False
    assert payment_plan["can_send_xlsx_password"] is False
    purpose = payment_plan_detail_context["purpose"]
    assert payment_plan["payment_plan_purposes"] == [{"id": str(purpose.id), "name": purpose.name}]
    group = payment_plan_detail_context["group"]
    assert payment_plan["payment_plan_group"] == {
        "id": str(group.id),
        "unicef_id": group.unicef_id,
        "name": group.name,
    }


def test_follow_ups_and_top_ups_return_correct_children(
    payment_plan_detail_context: dict[str, Any],
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        payment_plan_detail_context["user"],
        [Permissions.PM_VIEW_DETAILS],
        payment_plan_detail_context["business_area"],
        payment_plan_detail_context["program_active"],
    )
    pp = payment_plan_detail_context["pp"]
    top_up = PaymentPlanFactory(
        business_area=payment_plan_detail_context["business_area"],
        program_cycle=payment_plan_detail_context["cycle"],
        source_payment_plan=pp,
        plan_type=PaymentPlan.PlanType.TOP_UP,
    )
    follow_up = PaymentPlanFactory(
        business_area=payment_plan_detail_context["business_area"],
        program_cycle=payment_plan_detail_context["cycle"],
        source_payment_plan=pp,
        plan_type=PaymentPlan.PlanType.FOLLOW_UP,
    )

    response = payment_plan_detail_context["client"].get(payment_plan_detail_context["pp_detail_url"])
    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    top_up_ids = [p["id"] for p in data["top_ups"]]
    follow_up_ids = [p["id"] for p in data["follow_ups"]]
    assert top_up_ids == [str(top_up.id)]
    assert follow_up_ids == [str(follow_up.id)]


def test_has_fsp_delivery_mechanism_xlsx_template(
    payment_plan_detail_context: dict[str, Any],
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        payment_plan_detail_context["user"],
        [Permissions.PM_VIEW_DETAILS],
        payment_plan_detail_context["business_area"],
        payment_plan_detail_context["program_active"],
    )
    xlsx_temp = FinancialServiceProviderXlsxTemplateFactory()
    dm = DeliveryMechanismFactory()
    fsp = FinancialServiceProviderFactory(
        name="Test FSP 1",
        communication_channel=FinancialServiceProvider.COMMUNICATION_CHANNEL_XLSX,
        vision_vendor_number=123,
    )
    fsp.xlsx_templates.set([xlsx_temp])
    FspXlsxTemplatePerDeliveryMechanismFactory(
        financial_service_provider=fsp,
        delivery_mechanism=dm,
        xlsx_template=xlsx_temp,
    )
    payment_plan_detail_context["pp"].delivery_mechanism = dm
    payment_plan_detail_context["pp"].financial_service_provider = fsp
    payment_plan_detail_context["pp"].save()

    response = payment_plan_detail_context["client"].get(payment_plan_detail_context["pp_detail_url"])
    assert response.status_code == status.HTTP_200_OK
    payment_plan = response.json()
    assert payment_plan["has_fsp_delivery_mechanism_xlsx_template"] is True


def test_can_create_follow_up(
    payment_plan_detail_context: dict[str, Any],
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        payment_plan_detail_context["user"],
        [Permissions.PM_VIEW_DETAILS],
        payment_plan_detail_context["business_area"],
        payment_plan_detail_context["program_active"],
    )
    payment_plan_detail_context["pp"].plan_type = PaymentPlan.PlanType.FOLLOW_UP
    payment_plan_detail_context["pp"].save()

    response = payment_plan_detail_context["client"].get(payment_plan_detail_context["pp_detail_url"])
    assert response.status_code == status.HTTP_200_OK
    payment_plan = response.json()
    assert payment_plan["can_create_follow_up"] is False


def test_get_can_split(
    payment_plan_detail_context: dict[str, Any],
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        payment_plan_detail_context["user"],
        [Permissions.PM_VIEW_DETAILS],
        payment_plan_detail_context["business_area"],
        payment_plan_detail_context["program_active"],
    )
    PaymentPlanSplitFactory(payment_plan=payment_plan_detail_context["pp"], sent_to_payment_gateway=True)
    payment_plan_detail_context["pp"].status = PaymentPlan.Status.ACCEPTED
    payment_plan_detail_context["pp"].save()

    response = payment_plan_detail_context["client"].get(payment_plan_detail_context["pp_detail_url"])
    assert response.status_code == status.HTTP_200_OK
    payment_plan = response.json()
    assert payment_plan["can_split"] is False


def test_filter_by_status(payment_plan_filter_context: dict[str, Any]) -> None:
    response = payment_plan_filter_context["client"].get(
        payment_plan_filter_context["list_url"],
        {"status": PaymentPlan.Status.FINISHED.value},
    )
    payment_plan_filter_context["pp_finished"].refresh_from_db()
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()["results"]
    assert len(response_data) == 1
    assert response_data[0]["id"] == str(payment_plan_filter_context["pp_finished"].id)
    assert response_data[0]["status"] == "FINISHED"
    assert response_data[0]["name"] == "PP Filter Finished"

    response = payment_plan_filter_context["client"].get(
        payment_plan_filter_context["list_url"],
        {"status": PaymentPlan.Status.IN_APPROVAL.value},
    )
    payment_plan_filter_context["pp"].refresh_from_db()
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()["results"]
    assert len(response_data) == 1
    assert response_data[0]["id"] == str(payment_plan_filter_context["pp"].id)
    assert response_data[0]["status"] == "IN_APPROVAL"
    assert response_data[0]["name"] == "PP Filter Open"


def test_filter_by_program_cycle(
    payment_plan_filter_context: dict[str, Any],
) -> None:
    new_cycle = ProgramCycleFactory(program=payment_plan_filter_context["program_active"], title="Program Cycle ABC")
    new_pp = PaymentPlanFactory(
        name="TEST_ABC_123",
        business_area=payment_plan_filter_context["business_area"],
        program_cycle=new_cycle,
        status=PaymentPlan.Status.ACCEPTED,
        created_by=payment_plan_filter_context["user"],
    )
    response = payment_plan_filter_context["client"].get(
        payment_plan_filter_context["list_url"],
        {"program_cycle": new_pp.program_cycle.id},
    )
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()["results"]
    assert len(response_data) == 1
    assert response_data[0]["name"] == "TEST_ABC_123"
    assert response_data[0]["status"] == "ACCEPTED"


def test_filter_by_search(payment_plan_filter_context: dict[str, Any]) -> None:
    new_pp = PaymentPlanFactory(
        name="TEST_ABC_999",
        business_area=payment_plan_filter_context["business_area"],
        program_cycle=payment_plan_filter_context["cycle"],
        status=PaymentPlan.Status.ACCEPTED,
        created_by=payment_plan_filter_context["user"],
    )
    new_pp.unicef_id = "PP-SEARCH-0001"
    new_pp.save(update_fields=["unicef_id"])
    new_pp.refresh_from_db()
    response = payment_plan_filter_context["client"].get(
        payment_plan_filter_context["list_url"],
        {"search": "TEST_ABC"},
    )
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()["results"]
    assert len(response_data) == 1
    assert response_data[0]["name"] == "TEST_ABC_999"
    assert response_data[0]["status"] == "ACCEPTED"

    response = payment_plan_filter_context["client"].get(
        payment_plan_filter_context["list_url"],
        {"search": str(new_pp.id)},
    )
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()["results"]
    assert len(response_data) == 1
    assert response_data[0]["name"] == "TEST_ABC_999"

    response = payment_plan_filter_context["client"].get(
        payment_plan_filter_context["list_url"],
        {"search": "PP-SEARCH-0001"},
    )
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()["results"]
    assert len(response_data) == 1
    assert response_data[0]["name"] == "TEST_ABC_999"


def test_filter_by_entitled_quantity(payment_plan_filter_context: dict[str, Any]) -> None:
    PaymentPlanFactory(
        name="PP_1",
        business_area=payment_plan_filter_context["business_area"],
        program_cycle=payment_plan_filter_context["cycle"],
        status=PaymentPlan.Status.LOCKED_FSP,
        created_by=payment_plan_filter_context["user"],
        total_entitled_quantity=100,
    )
    PaymentPlanFactory(
        name="PP_2",
        business_area=payment_plan_filter_context["business_area"],
        program_cycle=payment_plan_filter_context["cycle"],
        status=PaymentPlan.Status.LOCKED_FSP,
        created_by=payment_plan_filter_context["user"],
        total_entitled_quantity=200,
    )
    response = payment_plan_filter_context["client"].get(
        payment_plan_filter_context["list_url"],
        {"total_entitled_quantity__gte": "99", "total_entitled_quantity__lte": 201},
    )
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()["results"]
    assert len(response_data) == 2
    assert response_data[0]["name"] == "PP_2"
    assert response_data[1]["name"] == "PP_1"

    response = payment_plan_filter_context["client"].get(
        payment_plan_filter_context["list_url"],
        {"total_entitled_quantity__lte": 101},
    )
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()["results"]
    assert len(response_data) == 1
    assert response_data[0]["name"] == "PP_1"


def test_filter_by_dispersion_date(payment_plan_filter_context: dict[str, Any]) -> None:
    PaymentPlanFactory(
        name="PP_abc",
        business_area=payment_plan_filter_context["business_area"],
        program_cycle=payment_plan_filter_context["cycle"],
        status=PaymentPlan.Status.LOCKED_FSP,
        created_by=payment_plan_filter_context["user"],
        dispersion_start_date="2022-02-24",
        dispersion_end_date="2022-03-03",
    )
    PaymentPlanFactory(
        name="PP_xyz",
        business_area=payment_plan_filter_context["business_area"],
        program_cycle=payment_plan_filter_context["cycle"],
        status=PaymentPlan.Status.LOCKED_FSP,
        created_by=payment_plan_filter_context["user"],
        dispersion_start_date="2022-01-01",
        dispersion_end_date="2022-01-17",
    )
    response = payment_plan_filter_context["client"].get(
        payment_plan_filter_context["list_url"],
        {"start_date": "2022-02-23", "end_date": "2022-03-04"},
    )
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()["results"]
    assert len(response_data) == 1
    assert response_data[0]["name"] == "PP_abc"

    response = payment_plan_filter_context["client"].get(
        payment_plan_filter_context["list_url"],
        {"end_date": "2022-01-18"},
    )
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()["results"]
    assert len(response_data) == 1
    assert response_data[0]["name"] == "PP_xyz"


def test_filter_by_plan_type_follow_up(payment_plan_filter_context: dict[str, Any]) -> None:
    PaymentPlanFactory(
        name="NEW_FOLLOW_up",
        plan_type=PaymentPlan.PlanType.FOLLOW_UP,
        business_area=payment_plan_filter_context["business_area"],
        program_cycle=payment_plan_filter_context["cycle"],
        status=PaymentPlan.Status.OPEN,
        created_by=payment_plan_filter_context["user"],
    )
    response = payment_plan_filter_context["client"].get(
        payment_plan_filter_context["list_url"],
        {"plan_type": PaymentPlan.PlanType.FOLLOW_UP},
    )
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()["results"]
    assert len(response_data) == 1
    assert response_data[0]["name"] == "NEW_FOLLOW_up"


def test_filter_by_plan_type_regular(payment_plan_filter_context: dict[str, Any]) -> None:
    PaymentPlanFactory(
        name="FOLLOW_UP_plan",
        plan_type=PaymentPlan.PlanType.FOLLOW_UP,
        business_area=payment_plan_filter_context["business_area"],
        program_cycle=payment_plan_filter_context["cycle"],
        status=PaymentPlan.Status.OPEN,
        created_by=payment_plan_filter_context["user"],
    )
    PaymentPlanFactory(
        name="TOP_UP_plan",
        plan_type=PaymentPlan.PlanType.TOP_UP,
        business_area=payment_plan_filter_context["business_area"],
        program_cycle=payment_plan_filter_context["cycle"],
        status=PaymentPlan.Status.OPEN,
        created_by=payment_plan_filter_context["user"],
    )
    response = payment_plan_filter_context["client"].get(
        payment_plan_filter_context["list_url"],
        {"plan_type": PaymentPlan.PlanType.REGULAR},
    )
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()["results"]
    returned_names = {r["name"] for r in response_data}
    assert returned_names == {"PP Filter Open", "PP Filter Finished"}


def test_filter_by_plan_type_top_up(payment_plan_filter_context: dict[str, Any]) -> None:
    PaymentPlanFactory(
        name="FOLLOW_UP_plan",
        plan_type=PaymentPlan.PlanType.FOLLOW_UP,
        business_area=payment_plan_filter_context["business_area"],
        program_cycle=payment_plan_filter_context["cycle"],
        status=PaymentPlan.Status.OPEN,
        created_by=payment_plan_filter_context["user"],
    )
    PaymentPlanFactory(
        name="TOP_UP_plan",
        plan_type=PaymentPlan.PlanType.TOP_UP,
        business_area=payment_plan_filter_context["business_area"],
        program_cycle=payment_plan_filter_context["cycle"],
        status=PaymentPlan.Status.OPEN,
        created_by=payment_plan_filter_context["user"],
    )
    response = payment_plan_filter_context["client"].get(
        payment_plan_filter_context["list_url"],
        {"plan_type": PaymentPlan.PlanType.TOP_UP},
    )
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()["results"]
    assert len(response_data) == 1
    assert response_data[0]["name"] == "TOP_UP_plan"


def test_filter_by_program(payment_plan_filter_context: dict[str, Any]) -> None:
    other_program = ProgramFactory(
        business_area=payment_plan_filter_context["business_area"],
        status=Program.ACTIVE,
    )
    other_cycle = ProgramCycleFactory(program=other_program)
    PaymentPlanFactory(
        name="PP Other Program",
        business_area=payment_plan_filter_context["business_area"],
        program_cycle=other_cycle,
        status=PaymentPlan.Status.OPEN,
        created_by=payment_plan_filter_context["user"],
    )
    response = payment_plan_filter_context["client"].get(
        payment_plan_filter_context["list_url"],
        {"program": payment_plan_filter_context["program_active"].code},
    )
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()["results"]
    assert len(response_data) == 2
    returned_names = {r["name"] for r in response_data}
    assert returned_names == {"PP Filter Open", "PP Filter Finished"}
    assert "PP Other Program" not in returned_names


def test_filter_by_payment_plan_group(
    payment_plan_filter_context: dict[str, Any],
) -> None:
    group = payment_plan_filter_context["pp"].payment_plan_group
    other_group = PaymentPlanGroupFactory(cycle=payment_plan_filter_context["cycle"])
    PaymentPlanFactory(
        business_area=payment_plan_filter_context["business_area"],
        program_cycle=payment_plan_filter_context["cycle"],
        payment_plan_group=other_group,
        created_by=payment_plan_filter_context["user"],
    )

    response = payment_plan_filter_context["client"].get(
        payment_plan_filter_context["list_url"],
        {"payment_plan_group": str(group.id)},
    )

    assert response.status_code == status.HTTP_200_OK
    results = response.json()["results"]
    assert len(results) == 2
    returned_ids = {r["id"] for r in results}
    assert str(payment_plan_filter_context["pp"].id) in returned_ids
    assert str(payment_plan_filter_context["pp_finished"].id) in returned_ids
