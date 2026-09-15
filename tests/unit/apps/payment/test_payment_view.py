from typing import Any

from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
import pytest
from rest_framework import status

from extras.test_utils.factories import (
    BeneficiaryGroupFactory,
    BusinessAreaFactory,
    DataCollectingTypeFactory,
    FinancialServiceProviderFactory,
    HouseholdFactory,
    IndividualFactory,
    IndividualRoleInHouseholdFactory,
    PaymentFactory,
    PaymentPlanFactory,
    ProgramCycleFactory,
    ProgramFactory,
    UserFactory,
)
from hope.apps.account.permissions import Permissions
from hope.apps.household.const import ROLE_ALTERNATE
from hope.models import DataCollectingType, Payment, PaymentPlan, Program

pytestmark = pytest.mark.django_db


@pytest.fixture
def business_area() -> Any:
    return BusinessAreaFactory(slug="afghanistan")


@pytest.fixture
def user() -> Any:
    return UserFactory()


@pytest.fixture
def program_active(business_area: Any) -> Program:
    return ProgramFactory(business_area=business_area, status=Program.ACTIVE, cycle=False)


@pytest.fixture
def cycle(program_active: Program) -> Any:
    return ProgramCycleFactory(program=program_active, title="Cycle Payments")


@pytest.fixture
def fsp_xlsx() -> Any:
    return FinancialServiceProviderFactory(
        name="Test FSP",
        vision_vendor_number="123",
        communication_channel="XLSX",
    )


@pytest.fixture
def payment_context(
    api_client: Any,
    business_area: Any,
    user: Any,
    program_active: Program,
    cycle: Any,
    fsp_xlsx: Any,
) -> dict[str, Any]:
    payment_plan = PaymentPlanFactory(
        name="Payment Plan",
        business_area=business_area,
        program_cycle=cycle,
        status=PaymentPlan.Status.DRAFT,
        created_by=user,
        financial_service_provider=fsp_xlsx,
    )
    payment = PaymentFactory(
        parent=payment_plan,
        status=Payment.STATUS_SUCCESS,
        delivered_quantity=999,
        entitlement_quantity=112,
        program=program_active,
        financial_service_provider=fsp_xlsx,
    )
    payment.refresh_from_db()

    url_kwargs = {
        "business_area_slug": business_area.slug,
        "program_code": program_active.code,
        "payment_plan_pk": payment_plan.pk,
    }
    url_kwargs_with_payment = {
        "business_area_slug": business_area.slug,
        "program_code": program_active.code,
        "payment_plan_pk": payment_plan.pk,
        "payment_id": payment.pk,
    }
    return {
        "business_area": business_area,
        "user": user,
        "program_active": program_active,
        "client": api_client(user),
        "payment_plan": payment_plan,
        "payment": payment,
        "url_list": reverse("api:payments:payments-list", kwargs=url_kwargs),
        "url_details": reverse("api:payments:payments-detail", kwargs=url_kwargs_with_payment),
        "url_mark_as_failed": reverse("api:payments:payments-mark-as-failed", kwargs=url_kwargs_with_payment),
        "url_revert_mark_as_failed": reverse(
            "api:payments:payments-revert-mark-as-failed",
            kwargs=url_kwargs_with_payment,
        ),
    }


@pytest.fixture
def not_eligible_payment_context(
    payment_context: dict[str, Any],
) -> dict[str, Any]:
    user = payment_context["user"]
    user.is_superuser = True
    user.save(update_fields=["is_superuser"])
    payment = payment_context["payment"]
    payment.status = Payment.STATUS_NOT_ELIGIBLE
    payment.conflicted = True
    payment.save(update_fields=["status", "conflicted"])
    excluded_payment = PaymentFactory(
        parent=payment_context["payment_plan"],
        program=payment_context["program_active"],
        status=Payment.STATUS_NOT_ELIGIBLE,
        excluded=True,
    )
    invalid_wallet_payment = PaymentFactory(
        parent=payment_context["payment_plan"],
        program=payment_context["program_active"],
        status=Payment.STATUS_NOT_ELIGIBLE,
        has_valid_wallet=False,
    )
    url_kwargs = {
        "business_area_slug": payment_context["business_area"].slug,
        "program_code": payment_context["program_active"].code,
        "payment_plan_pk": payment_context["payment_plan"].pk,
    }
    return {
        **payment_context,
        "excluded_payment": excluded_payment,
        "invalid_wallet_payment": invalid_wallet_payment,
        "url_not_eligible": reverse("api:payments:payments-not-eligible", kwargs=url_kwargs),
        "url_not_eligible_count": reverse("api:payments:payments-not-eligible-count", kwargs=url_kwargs),
    }


@pytest.fixture
def authorized_payment_context(
    payment_context: dict[str, Any],
    create_user_role_with_permissions: Any,
) -> dict[str, Any]:
    create_user_role_with_permissions(
        payment_context["user"],
        [Permissions.PM_VIEW_DETAILS],
        payment_context["business_area"],
        payment_context["program_active"],
    )
    return payment_context


@pytest.fixture
def non_super_not_eligible_payment_context(
    authorized_payment_context: dict[str, Any],
) -> dict[str, Any]:
    Payment.objects.filter(pk=authorized_payment_context["payment"].pk).update(status=Payment.STATUS_NOT_ELIGIBLE)
    return authorized_payment_context


@pytest.fixture
def payment_people_context(
    api_client: Any,
    business_area: Any,
    user: Any,
) -> dict[str, Any]:
    data_collecting_type = DataCollectingTypeFactory(type=DataCollectingType.Type.SOCIAL)
    beneficiary_group = BeneficiaryGroupFactory(master_detail=False)
    program = ProgramFactory(
        business_area=business_area,
        status=Program.ACTIVE,
        data_collecting_type=data_collecting_type,
        beneficiary_group=beneficiary_group,
        cycle=False,
    )
    cycle = ProgramCycleFactory(program=program, title="Cycle Payments People")
    payment_plan = PaymentPlanFactory(
        name="Payment Plan",
        business_area=business_area,
        program_cycle=cycle,
        status=PaymentPlan.Status.DRAFT,
        created_by=user,
    )
    head = IndividualFactory(
        full_name="Full Name Test123",
        household=None,
        program=program,
        business_area=business_area,
    )
    household = HouseholdFactory(
        head_of_household=head,
        program=program,
        business_area=business_area,
        size=2,
        create_role=False,
    )
    IndividualRoleInHouseholdFactory(household=household, individual=head, role=ROLE_ALTERNATE)
    payment = PaymentFactory(
        parent=payment_plan,
        status=Payment.STATUS_SUCCESS,
        delivered_quantity=999,
        entitlement_quantity=112,
        program=program,
        household=household,
        head_of_household=head,
        collector=head,
    )

    url_kwargs = {
        "business_area_slug": business_area.slug,
        "program_code": program.code,
        "payment_plan_pk": payment_plan.pk,
    }
    return {
        "business_area": business_area,
        "user": user,
        "program_active": program,
        "client": api_client(user),
        "payment_plan": payment_plan,
        "payment": payment,
        "url_list": reverse("api:payments:payments-list", kwargs=url_kwargs),
    }


@pytest.mark.parametrize(
    ("permissions", "expected_status"),
    [
        ([Permissions.PM_VIEW_DETAILS], status.HTTP_200_OK),
        ([], status.HTTP_403_FORBIDDEN),
    ],
)
def test_get_list(
    payment_context: dict[str, Any],
    permissions: list,
    expected_status: int,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        payment_context["user"],
        permissions,
        payment_context["business_area"],
        payment_context["program_active"],
    )
    response = payment_context["client"].get(payment_context["url_list"])

    assert response.status_code == expected_status
    if expected_status == status.HTTP_200_OK:
        resp_data = response.json()
        assert len(resp_data["results"]) == 1
        payment = resp_data["results"][0]
        assert payment["delivered_quantity"] == "999.00"
        assert payment["status"] == "Transaction Successful"


def test_get_list_for_people(
    payment_people_context: dict[str, Any],
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        payment_people_context["user"],
        [Permissions.PM_VIEW_DETAILS],
        payment_people_context["business_area"],
        payment_people_context["program_active"],
    )
    assert payment_people_context["payment_plan"].is_social_worker_program is True

    response = payment_people_context["client"].get(payment_people_context["url_list"])

    assert response.status_code == status.HTTP_200_OK
    resp_data = response.json()
    assert len(resp_data["results"]) == 1
    payment = resp_data["results"][0]
    assert payment.get("people_individual") is not None
    assert payment["people_individual"]["full_name"] == "Full Name Test123"
    assert payment["people_individual"]["role"] == "Alternate collector"


@pytest.mark.parametrize(
    ("permissions", "expected_status"),
    [
        ([Permissions.PM_VIEW_DETAILS], status.HTTP_200_OK),
        ([], status.HTTP_403_FORBIDDEN),
    ],
)
def test_details(
    payment_context: dict[str, Any],
    permissions: list,
    expected_status: int,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        payment_context["user"],
        permissions,
        payment_context["business_area"],
        payment_context["program_active"],
    )
    with CaptureQueriesContext(connection) as captured_queries:
        response = payment_context["client"].get(payment_context["url_details"])

    assert response.status_code == expected_status
    assert "available_count" not in " ".join(query["sql"] for query in captured_queries.captured_queries)
    if expected_status == status.HTTP_200_OK:
        resp_data = response.json()
        assert "id" in resp_data
        assert resp_data["delivered_quantity"] == "999.00"
        assert resp_data["status"] == "Transaction Successful"
        assert set(resp_data["parent"]) == {
            "id",
            "unicef_id",
            "name",
            "status",
            "plan_type",
            "is_payment_gateway",
            "delivery_mechanism",
            "payment_verification_plans",
        }


@pytest.mark.parametrize(
    ("permissions", "expected_status"),
    [
        ([Permissions.PM_MARK_PAYMENT_AS_FAILED], status.HTTP_200_OK),
        ([], status.HTTP_403_FORBIDDEN),
    ],
)
def test_mark_as_failed(
    payment_context: dict[str, Any],
    permissions: list,
    expected_status: int,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        payment_context["user"],
        permissions,
        payment_context["business_area"],
        payment_context["program_active"],
    )
    response = payment_context["client"].get(payment_context["url_mark_as_failed"])

    assert response.status_code == expected_status
    if expected_status == status.HTTP_200_OK:
        resp_data = response.json()
        assert "id" in resp_data
        assert resp_data["delivered_quantity"] == "0.00"
        assert resp_data["status"] == "Force failed"


@pytest.mark.parametrize(
    ("permissions", "expected_status"),
    [
        ([Permissions.PM_MARK_PAYMENT_AS_FAILED], status.HTTP_200_OK),
        ([], status.HTTP_403_FORBIDDEN),
    ],
)
def test_revert_mark_as_failed(
    payment_context: dict[str, Any],
    permissions: list,
    expected_status: int,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        payment_context["user"],
        permissions,
        payment_context["business_area"],
        payment_context["program_active"],
    )
    payment_context["payment"].status = Payment.STATUS_FORCE_FAILED
    payment_context["payment"].save()
    response = payment_context["client"].post(
        payment_context["url_revert_mark_as_failed"],
        {"delivered_quantity": "111.00", "delivery_date": "2024-01-01"},
    )
    assert response.status_code == expected_status
    if expected_status == status.HTTP_200_OK:
        resp_data = response.json()
        assert "id" in resp_data
        assert resp_data["delivered_quantity"] == "111.00"
        assert resp_data["status"] == "Partially Distributed"
        assert resp_data["delivery_date"] == "2024-01-01"


def test_filter_by_household_unicef_id(
    payment_context: dict[str, Any],
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        payment_context["user"],
        [Permissions.PM_VIEW_DETAILS],
        payment_context["business_area"],
        payment_context["program_active"],
    )
    response = payment_context["client"].get(
        payment_context["url_list"] + f"?household_unicef_id={payment_context['payment'].household.unicef_id}"
    )

    assert response.status_code == status.HTTP_200_OK
    resp_data = response.json()
    assert len(resp_data["results"]) == 1
    payment = resp_data["results"][0]
    assert payment["household_unicef_id"] == payment_context["payment"].household.unicef_id


def test_filter_by_collector_full_name(
    payment_context: dict[str, Any],
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        payment_context["user"],
        [Permissions.PM_VIEW_DETAILS],
        payment_context["business_area"],
        payment_context["program_active"],
    )
    collector_full_name = payment_context["payment"].collector.full_name
    response = payment_context["client"].get(
        payment_context["url_list"] + f"?collector_full_name={collector_full_name[:5]}"
    )

    assert response.status_code == status.HTTP_200_OK
    resp_data = response.json()
    assert len(resp_data["results"]) == 1
    payment = resp_data["results"][0]
    assert payment["household_unicef_id"] == payment_context["payment"].household.unicef_id
    assert (
        Payment.objects.get(unicef_id=payment["unicef_id"]).collector.full_name
        == payment_context["payment"].collector.full_name
    )


def test_filter_by_collector_latin_full_name(
    payment_context: dict[str, Any],
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        payment_context["user"],
        [Permissions.PM_VIEW_DETAILS],
        payment_context["business_area"],
        payment_context["program_active"],
    )
    collector = payment_context["payment"].collector
    collector.full_name = "Анна Ковальська"
    collector.full_name_latin = "Anna Kovalska"
    collector.save(update_fields=["full_name", "full_name_latin"])

    response = payment_context["client"].get(payment_context["url_list"] + "?collector_full_name=Anna Kov")

    assert response.status_code == status.HTTP_200_OK
    resp_data = response.json()
    assert len(resp_data["results"]) == 1
    assert resp_data["results"][0]["household_unicef_id"] == payment_context["payment"].household.unicef_id


def test_filter_by_payment_unicef_id(
    payment_context: dict[str, Any],
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        payment_context["user"],
        [Permissions.PM_VIEW_DETAILS],
        payment_context["business_area"],
        payment_context["program_active"],
    )
    response = payment_context["client"].get(
        payment_context["url_list"] + f"?payment_unicef_id={payment_context['payment'].unicef_id}"
    )

    assert response.status_code == status.HTTP_200_OK
    resp_data = response.json()
    assert len(resp_data["results"]) == 1
    payment = resp_data["results"][0]
    assert payment["unicef_id"] == payment_context["payment"].unicef_id


def test_filter_by_raw_payment_status(
    authorized_payment_context: dict[str, Any],
) -> None:
    response = authorized_payment_context["client"].get(
        authorized_payment_context["url_list"],
        {"status": Payment.STATUS_SUCCESS},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["results"][0]["id"] == str(authorized_payment_context["payment"].id)
    assert len(response.json()["results"]) == 1


def test_not_eligible_status_is_rejected_by_eligible_payment_filter(
    authorized_payment_context: dict[str, Any],
) -> None:
    response = authorized_payment_context["client"].get(
        authorized_payment_context["url_list"],
        {"status": Payment.STATUS_NOT_ELIGIBLE},
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_superuser_can_list_not_eligible_payments_and_filter_causes_with_or_logic(
    not_eligible_payment_context: dict[str, Any],
) -> None:
    url = (
        not_eligible_payment_context["url_not_eligible"]
        + "?ineligibility_cause=conflicted&ineligibility_cause=invalid_wallet"
    )

    with CaptureQueriesContext(connection) as captured_queries:
        response = not_eligible_payment_context["client"].get(url)

    assert response.status_code == status.HTTP_200_OK
    assert len(captured_queries) <= 30
    results = response.json()["results"]
    assert sorted([results[0]["id"], results[1]["id"]]) == sorted(
        [
            str(not_eligible_payment_context["payment"].id),
            str(not_eligible_payment_context["invalid_wallet_payment"].id),
        ]
    )


def test_not_eligible_payment_response_exposes_eligibility_flags(
    not_eligible_payment_context: dict[str, Any],
) -> None:
    response = not_eligible_payment_context["client"].get(
        not_eligible_payment_context["url_not_eligible"] + "?ineligibility_cause=invalid_wallet"
    )

    assert response.status_code == status.HTTP_200_OK
    result = response.json()["results"][0]
    assert result["id"] == str(not_eligible_payment_context["invalid_wallet_payment"].id)
    assert result["conflicted"] is False
    assert result["excluded"] is False
    assert result["has_valid_wallet"] is False


def test_superuser_can_count_not_eligible_payments(
    not_eligible_payment_context: dict[str, Any],
) -> None:
    response = not_eligible_payment_context["client"].get(not_eligible_payment_context["url_not_eligible_count"])

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"count": 3}


@pytest.mark.parametrize("url_name", ["payments-not-eligible", "payments-not-eligible-count"])
def test_non_superuser_cannot_access_not_eligible_payment_collections(
    authorized_payment_context: dict[str, Any],
    url_name: str,
) -> None:
    url = reverse(
        f"api:payments:{url_name}",
        kwargs={
            "business_area_slug": authorized_payment_context["business_area"].slug,
            "program_code": authorized_payment_context["program_active"].code,
            "payment_plan_pk": authorized_payment_context["payment_plan"].pk,
        },
    )

    response = authorized_payment_context["client"].get(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_non_superuser_cannot_retrieve_not_eligible_payment(
    non_super_not_eligible_payment_context: dict[str, Any],
) -> None:
    response = non_super_not_eligible_payment_context["client"].get(
        non_super_not_eligible_payment_context["url_details"]
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_filter_by_individual_unicef_id(
    payment_people_context: dict[str, Any],
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        payment_people_context["user"],
        [Permissions.PM_VIEW_DETAILS],
        payment_people_context["business_area"],
        payment_people_context["program_active"],
    )
    payment_people_context["program_active"].data_collecting_type.type = DataCollectingType.Type.SOCIAL
    payment_people_context["program_active"].data_collecting_type.save()
    payment_people_context["payment_plan"].refresh_from_db()
    assert payment_people_context["payment_plan"].is_social_worker_program is True
    ind = payment_people_context["payment"].household.head_of_household
    response = payment_people_context["client"].get(
        payment_people_context["url_list"] + f"?individual_unicef_id={ind.unicef_id}"
    )

    assert response.status_code == status.HTTP_200_OK
    resp_data = response.json()
    assert len(resp_data["results"]) == 1
    payment = resp_data["results"][0]
    assert payment["unicef_id"] == payment_people_context["payment"].unicef_id


def test_extra_fields_in_payment_detail_api(
    payment_context: dict[str, Any],
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        payment_context["user"],
        [Permissions.PM_VIEW_DETAILS],
        payment_context["business_area"],
        payment_context["program_active"],
    )
    payment_obj = payment_context["payment"]
    payment_obj.extras = {
        "extra_fields": {
            "custom_field_1": "value1",
            "custom_field_2": 123,
        }
    }
    payment_obj.save()

    response = payment_context["client"].get(payment_context["url_details"])

    assert response.status_code == status.HTTP_200_OK
    resp_data = response.json()
    assert resp_data["extra_fields"] == {"custom_field_1": "value1", "custom_field_2": 123}
    assert "extras" not in resp_data
