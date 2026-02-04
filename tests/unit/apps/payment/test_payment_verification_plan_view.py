from io import BytesIO
from pathlib import Path
from typing import Any

from django.conf import settings
from django.urls import reverse
from django.utils import timezone
import pytest
from rest_framework import status

from extras.test_utils.factories import (
    BusinessAreaFactory,
    PaymentFactory,
    PaymentPlanFactory,
    PaymentVerificationFactory,
    PaymentVerificationPlanFactory,
    ProgramCycleFactory,
    ProgramFactory,
    UserFactory,
)
from hope.apps.account.permissions import Permissions
from hope.models import (
    Payment,
    PaymentPlan,
    PaymentVerification,
    PaymentVerificationPlan,
    Program,
    build_summary,
)

pytestmark = pytest.mark.django_db


@pytest.fixture
def business_area() -> Any:
    return BusinessAreaFactory(slug="afghanistan")


@pytest.fixture
def user() -> Any:
    return UserFactory()


@pytest.fixture
def program_active(business_area: Any) -> Program:
    return ProgramFactory(business_area=business_area, status=Program.ACTIVE)


@pytest.fixture
def cycle(program_active: Program) -> Any:
    return ProgramCycleFactory(program=program_active, title="Cycle Verification")


@pytest.fixture
def verification_context(
    api_client: Any,
    business_area: Any,
    user: Any,
    program_active: Program,
    cycle: Any,
) -> dict[str, Any]:
    payment_plan = PaymentPlanFactory(
        name="Payment Plan",
        business_area=business_area,
        program_cycle=cycle,
        status=PaymentPlan.Status.FINISHED,
        created_by=user,
    )
    build_summary(payment_plan)

    payment_1 = PaymentFactory(
        pk="0329a41f-affd-4669-9e38-38ec2d6699b3",
        parent=payment_plan,
        status=Payment.STATUS_SUCCESS,
        delivered_quantity=999,
        entitlement_quantity=112,
    )
    payment_2 = PaymentFactory(
        pk="299811ef-b123-427d-b77d-9fd5d1bc8946",
        parent=payment_plan,
        status=Payment.STATUS_SUCCESS,
        delivered_quantity=111,
        entitlement_quantity=112,
    )
    pvp = PaymentVerificationPlanFactory(
        payment_plan=payment_plan,
        sampling=PaymentVerificationPlan.SAMPLING_RANDOM,
        verification_channel=PaymentVerificationPlan.VERIFICATION_CHANNEL_MANUAL,
    )
    verification_1 = PaymentVerificationFactory(
        payment_verification_plan=pvp,
        payment=payment_1,
        status=PaymentVerification.STATUS_RECEIVED_WITH_ISSUES,
        status_date=timezone.now(),
    )
    verification_2 = PaymentVerificationFactory(
        payment_verification_plan=pvp,
        payment=payment_2,
        status=PaymentVerification.STATUS_RECEIVED_WITH_ISSUES,
        status_date=timezone.now(),
    )

    client = api_client(user)
    url_kwargs = {
        "business_area_slug": business_area.slug,
        "program_slug": program_active.slug,
        "pk": str(payment_plan.pk),
    }
    url_kwargs_id = {
        "business_area_slug": business_area.slug,
        "program_slug": program_active.slug,
        "pk": str(payment_plan.pk),
        "verification_plan_id": str(pvp.pk),
    }

    return {
        "business_area": business_area,
        "user": user,
        "client": client,
        "program_active": program_active,
        "payment_plan": payment_plan,
        "payment_1": payment_1,
        "payment_2": payment_2,
        "pvp": pvp,
        "verification_1": verification_1,
        "verification_2": verification_2,
        "url_list": reverse(
            "api:payments:payment-verifications-list",
            kwargs={
                "business_area_slug": business_area.slug,
                "program_slug": program_active.slug,
            },
        ),
        "url_details": reverse("api:payments:payment-verifications-detail", kwargs=url_kwargs),
        "url_create": reverse(
            "api:payments:payment-verifications-create-payment-verification-plan",
            kwargs=url_kwargs,
        ),
        "url_update": reverse(
            "api:payments:payment-verifications-update-payment-verification-plan",
            kwargs=url_kwargs_id,
        ),
        "url_activate": reverse(
            "api:payments:payment-verifications-activate-payment-verification-plan",
            kwargs=url_kwargs_id,
        ),
        "url_finish": reverse(
            "api:payments:payment-verifications-finish-payment-verification-plan",
            kwargs=url_kwargs_id,
        ),
        "url_discard": reverse(
            "api:payments:payment-verifications-discard-payment-verification-plan",
            kwargs=url_kwargs_id,
        ),
        "url_invalid": reverse(
            "api:payments:payment-verifications-invalid-payment-verification-plan",
            kwargs=url_kwargs_id,
        ),
        "url_delete": reverse(
            "api:payments:payment-verifications-delete-payment-verification-plan",
            kwargs=url_kwargs_id,
        ),
        "url_export_xlsx": reverse(
            "api:payments:payment-verifications-export-xlsx-payment-verification-plan",
            kwargs=url_kwargs_id,
        ),
        "url_import_xlsx": reverse(
            "api:payments:payment-verifications-import-xlsx-payment-verification-plan",
            kwargs=url_kwargs_id,
        ),
    }


@pytest.mark.parametrize(
    ("permissions", "expected_status"),
    [
        ([Permissions.PAYMENT_VERIFICATION_VIEW_LIST], status.HTTP_200_OK),
        ([], status.HTTP_403_FORBIDDEN),
    ],
)
def test_get_list(
    verification_context: dict[str, Any],
    permissions: list,
    expected_status: int,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        verification_context["user"],
        permissions,
        verification_context["business_area"],
        verification_context["program_active"],
    )
    response = verification_context["client"].get(verification_context["url_list"])

    assert response.status_code == expected_status
    if expected_status == status.HTTP_200_OK:
        resp_data = response.json()
        assert len(resp_data["results"]) == 1
        pv = resp_data["results"][0]
        assert pv["verification_status"] == "PENDING"


@pytest.mark.parametrize(
    ("permissions", "expected_status"),
    [
        ([Permissions.PAYMENT_VERIFICATION_VIEW_DETAILS], status.HTTP_200_OK),
        ([], status.HTTP_403_FORBIDDEN),
    ],
)
def test_details(
    verification_context: dict[str, Any],
    permissions: list,
    expected_status: int,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        verification_context["user"],
        permissions,
        verification_context["business_area"],
        verification_context["program_active"],
    )
    response = verification_context["client"].get(verification_context["url_details"])

    assert response.status_code == expected_status
    if expected_status == status.HTTP_200_OK:
        resp_data = response.json()
        assert "id" in resp_data
        assert resp_data["available_payment_records_count"] == 2
        assert resp_data["eligible_payments_count"] == 2
        assert resp_data["payment_verification_plans"][0]["status"] == PaymentVerificationPlan.STATUS_PENDING
        assert resp_data["payment_verification_plans"][0]["sampling"] == "Random sampling"
        assert (
            resp_data["payment_verification_plans"][0]["verification_channel"]
            == PaymentVerificationPlan.VERIFICATION_CHANNEL_MANUAL
        )
        assert resp_data["payment_verification_summary"]["status"] == "PENDING"


@pytest.mark.parametrize(
    ("permissions", "expected_status"),
    [
        ([Permissions.PAYMENT_VERIFICATION_CREATE], status.HTTP_201_CREATED),
        ([], status.HTTP_403_FORBIDDEN),
    ],
)
def test_create_pvp(
    verification_context: dict[str, Any],
    permissions: list,
    expected_status: int,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        verification_context["user"],
        permissions,
        verification_context["business_area"],
        verification_context["program_active"],
    )
    PaymentFactory(
        parent=verification_context["payment_plan"],
        status=Payment.STATUS_SUCCESS,
        delivered_quantity=111,
        entitlement_quantity=112,
    )
    response = verification_context["client"].post(
        verification_context["url_create"],
        {
            "sampling": "FULL_LIST",
            "full_list_arguments": {"excluded_admin_areas": []},
            "verification_channel": PaymentVerificationPlan.VERIFICATION_CHANNEL_XLSX,
            "rapid_pro_arguments": None,
            "random_sampling_arguments": None,
        },
        format="json",
    )
    assert response.status_code == expected_status
    if expected_status == status.HTTP_201_CREATED:
        resp_data = response.json()
        assert "id" in resp_data
        assert len(resp_data["payment_verification_plans"]) == 2
        pvp = resp_data["payment_verification_plans"][1]
        assert pvp["status"] == PaymentVerificationPlan.STATUS_PENDING
        assert pvp["verification_channel"] == PaymentVerificationPlan.VERIFICATION_CHANNEL_XLSX
        assert pvp["sampling"] == "Full list"
        assert pvp["excluded_admin_areas_filter"] == []
        assert resp_data["payment_verification_summary"]["status"] == "PENDING"


def test_create_pvp_validation_error_no_records(
    verification_context: dict[str, Any],
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        verification_context["user"],
        [Permissions.PAYMENT_VERIFICATION_CREATE],
        verification_context["business_area"],
        verification_context["program_active"],
    )
    response = verification_context["client"].post(
        verification_context["url_create"],
        {
            "sampling": "FULL_LIST",
            "full_list_arguments": {"excluded_admin_areas": []},
            "verification_channel": PaymentVerificationPlan.VERIFICATION_CHANNEL_XLSX,
            "rapid_pro_arguments": None,
            "random_sampling_arguments": None,
        },
        format="json",
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "There are no payment records that could be assigned to a new verification plan" in response.json()[0]


@pytest.mark.parametrize(
    ("permissions", "expected_status"),
    [
        ([Permissions.PAYMENT_VERIFICATION_UPDATE], status.HTTP_200_OK),
        ([], status.HTTP_403_FORBIDDEN),
    ],
)
def test_update_pvp(
    verification_context: dict[str, Any],
    permissions: list,
    expected_status: int,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        verification_context["user"],
        permissions,
        verification_context["business_area"],
        verification_context["program_active"],
    )
    response = verification_context["client"].patch(
        verification_context["url_update"],
        {
            "sampling": "FULL_LIST",
            "full_list_arguments": {"excluded_admin_areas": []},
            "verification_channel": "MANUAL",
            "rapid_pro_arguments": None,
            "random_sampling_arguments": None,
        },
        format="json",
    )
    assert response.status_code == expected_status
    if expected_status == status.HTTP_200_OK:
        resp_data = response.json()
        assert "id" in resp_data
        assert len(resp_data["payment_verification_plans"]) == 1
        pvp = resp_data["payment_verification_plans"][0]
        assert pvp["status"] == PaymentVerificationPlan.STATUS_PENDING
        assert pvp["verification_channel"] == "MANUAL"
        assert pvp["sampling"] == "Full list"
        assert pvp["excluded_admin_areas_filter"] == []
        assert resp_data["payment_verification_summary"]["status"] == "PENDING"


@pytest.mark.parametrize(
    ("permissions", "expected_status"),
    [
        ([Permissions.PAYMENT_VERIFICATION_ACTIVATE], status.HTTP_200_OK),
        ([], status.HTTP_403_FORBIDDEN),
    ],
)
def test_pvp_activate(
    verification_context: dict[str, Any],
    permissions: list,
    expected_status: int,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        verification_context["user"],
        permissions,
        verification_context["business_area"],
        verification_context["program_active"],
    )
    response = verification_context["client"].post(
        verification_context["url_activate"],
        {"version": verification_context["pvp"].version},
        format="json",
    )
    assert response.status_code == expected_status
    if expected_status == status.HTTP_200_OK:
        resp_data = response.json()
        assert "id" in resp_data
        assert len(resp_data["payment_verification_plans"]) == 1
        assert resp_data["payment_verification_plans"][0]["status"] == PaymentVerificationPlan.STATUS_ACTIVE


@pytest.mark.parametrize(
    ("permissions", "expected_status"),
    [
        ([Permissions.PAYMENT_VERIFICATION_FINISH], status.HTTP_200_OK),
        ([], status.HTTP_403_FORBIDDEN),
    ],
)
def test_pvp_finish(
    verification_context: dict[str, Any],
    permissions: list,
    expected_status: int,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        verification_context["user"],
        permissions,
        verification_context["business_area"],
        verification_context["program_active"],
    )
    verification_context["pvp"].status = PaymentVerificationPlan.STATUS_ACTIVE
    verification_context["pvp"].save()
    response = verification_context["client"].post(
        verification_context["url_finish"],
        {"version": verification_context["pvp"].version},
        format="json",
    )
    assert response.status_code == expected_status
    if expected_status == status.HTTP_200_OK:
        resp_data = response.json()
        assert "id" in resp_data
        assert len(resp_data["payment_verification_plans"]) == 1
        assert resp_data["payment_verification_plans"][0]["status"] == PaymentVerificationPlan.STATUS_FINISHED


def test_pvp_finish_validation_error(
    verification_context: dict[str, Any],
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        verification_context["user"],
        [Permissions.PAYMENT_VERIFICATION_FINISH],
        verification_context["business_area"],
        verification_context["program_active"],
    )
    response = verification_context["client"].post(
        verification_context["url_finish"],
        {"version": verification_context["pvp"].version},
        format="json",
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "You can finish only ACTIVE verification" in response.json()


@pytest.mark.parametrize(
    ("permissions", "expected_status"),
    [
        ([Permissions.PAYMENT_VERIFICATION_DISCARD], status.HTTP_200_OK),
        ([], status.HTTP_403_FORBIDDEN),
    ],
)
def test_pvp_discard(
    verification_context: dict[str, Any],
    permissions: list,
    expected_status: int,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        verification_context["user"],
        permissions,
        verification_context["business_area"],
        verification_context["program_active"],
    )
    verification_context["pvp"].status = PaymentVerificationPlan.STATUS_ACTIVE
    verification_context["pvp"].save()
    response = verification_context["client"].post(
        verification_context["url_discard"],
        {"version": verification_context["pvp"].version},
        format="json",
    )
    assert response.status_code == expected_status
    if expected_status == status.HTTP_200_OK:
        resp_data = response.json()
        assert "id" in resp_data
        assert len(resp_data["payment_verification_plans"]) == 1
        assert resp_data["payment_verification_plans"][0]["status"] == PaymentVerificationPlan.STATUS_PENDING


@pytest.mark.parametrize(
    ("permissions", "expected_status"),
    [
        ([Permissions.PAYMENT_VERIFICATION_INVALID], status.HTTP_200_OK),
        ([], status.HTTP_403_FORBIDDEN),
    ],
)
def test_pvp_invalid(
    verification_context: dict[str, Any],
    permissions: list,
    expected_status: int,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        verification_context["user"],
        permissions,
        verification_context["business_area"],
        verification_context["program_active"],
    )
    verification_context["pvp"].status = PaymentVerificationPlan.STATUS_ACTIVE
    verification_context["pvp"].verification_channel = PaymentVerificationPlan.VERIFICATION_CHANNEL_XLSX
    verification_context["pvp"].xlsx_file_imported = True
    verification_context["pvp"].save()
    response = verification_context["client"].post(
        verification_context["url_invalid"],
        {"version": verification_context["pvp"].version},
        format="json",
    )
    assert response.status_code == expected_status
    if expected_status == status.HTTP_200_OK:
        resp_data = response.json()
        assert "id" in resp_data
        assert len(resp_data["payment_verification_plans"]) == 1
        assert resp_data["payment_verification_plans"][0]["status"] == PaymentVerificationPlan.STATUS_INVALID


@pytest.mark.parametrize(
    ("permissions", "expected_status"),
    [
        ([Permissions.PAYMENT_VERIFICATION_DELETE], status.HTTP_200_OK),
        ([], status.HTTP_403_FORBIDDEN),
    ],
)
def test_pvp_delete(
    verification_context: dict[str, Any],
    permissions: list,
    expected_status: int,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        verification_context["user"],
        permissions,
        verification_context["business_area"],
        verification_context["program_active"],
    )
    response = verification_context["client"].post(
        verification_context["url_delete"],
        {"version": verification_context["pvp"].version},
        format="json",
    )
    assert response.status_code == expected_status
    if expected_status == status.HTTP_200_OK:
        resp_data = response.json()
        assert "id" in resp_data
        assert len(resp_data["payment_verification_plans"]) == 0


@pytest.mark.parametrize(
    ("permissions", "expected_status"),
    [
        ([Permissions.PAYMENT_VERIFICATION_EXPORT], status.HTTP_200_OK),
        ([], status.HTTP_403_FORBIDDEN),
    ],
)
def test_pvp_export_xlsx(
    verification_context: dict[str, Any],
    permissions: list,
    expected_status: int,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        verification_context["user"],
        permissions,
        verification_context["business_area"],
        verification_context["program_active"],
    )
    verification_context["pvp"].status = PaymentVerificationPlan.STATUS_ACTIVE
    verification_context["pvp"].verification_channel = PaymentVerificationPlan.VERIFICATION_CHANNEL_XLSX
    verification_context["pvp"].save()
    response = verification_context["client"].post(
        verification_context["url_export_xlsx"],
        {"version": verification_context["pvp"].version},
        format="json",
    )
    assert response.status_code == expected_status
    if expected_status == status.HTTP_200_OK:
        resp_data = response.json()
        assert "id" in resp_data
        assert len(resp_data["payment_verification_plans"]) == 1
        verification_context["pvp"].refresh_from_db()
        if not verification_context["pvp"].xlsx_file_exporting:
            assert verification_context["pvp"].has_xlsx_payment_verification_plan_file is True
        else:
            assert resp_data["payment_verification_plans"][0]["xlsx_file_exporting"] is True


@pytest.mark.parametrize(
    ("permissions", "expected_status"),
    [
        ([Permissions.PAYMENT_VERIFICATION_IMPORT], status.HTTP_200_OK),
        ([], status.HTTP_403_FORBIDDEN),
    ],
)
def test_pvp_import_xlsx(
    verification_context: dict[str, Any],
    permissions: list,
    expected_status: int,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        verification_context["user"],
        permissions,
        verification_context["business_area"],
        verification_context["program_active"],
    )
    verification_context["pvp"].status = PaymentVerificationPlan.STATUS_ACTIVE
    verification_context["pvp"].verification_channel = PaymentVerificationPlan.VERIFICATION_CHANNEL_XLSX
    verification_context["pvp"].save()
    file = BytesIO(Path(f"{settings.TESTS_ROOT}/apps/payment/test_file/unordered_columns_1.xlsx").read_bytes())
    file.name = "unordered_columns_1.xlsx"
    response = verification_context["client"].post(
        verification_context["url_import_xlsx"],
        {"version": verification_context["pvp"].version, "file": file},
        format="multipart",
    )
    assert response.status_code == expected_status
    if expected_status == status.HTTP_200_OK:
        resp_data = response.json()
        assert "id" in resp_data
        assert len(resp_data["payment_verification_plans"]) == 1
        assert resp_data["payment_verification_plans"][0]["xlsx_file_imported"] is True


@pytest.mark.parametrize(
    ("permissions", "expected_status"),
    [
        ([Permissions.PAYMENT_VERIFICATION_VIEW_DETAILS], status.HTTP_200_OK),
        ([], status.HTTP_403_FORBIDDEN),
    ],
)
def test_verifications_list(
    verification_context: dict[str, Any],
    permissions: list,
    expected_status: int,
    create_user_role_with_permissions: Any,
) -> None:
    url = reverse(
        "api:payments:verification-records-list",
        kwargs={
            "business_area_slug": verification_context["business_area"].slug,
            "program_slug": verification_context["program_active"].slug,
            "payment_verification_pk": str(verification_context["payment_plan"].pk),
        },
    )
    create_user_role_with_permissions(
        verification_context["user"],
        permissions,
        verification_context["business_area"],
        verification_context["program_active"],
    )
    response = verification_context["client"].get(url)

    assert response.status_code == expected_status
    if expected_status == status.HTTP_200_OK:
        resp_data = response.json()["results"]
        assert len(resp_data) == 2
        payment = resp_data[0]
        assert "id" in payment
        assert "verification" in payment
        assert "id" in payment["verification"]
        assert "status" in payment["verification"]
        assert "verification_channel" in payment["verification"]
        assert "received_amount" in payment["verification"]


@pytest.mark.parametrize(
    ("permissions", "expected_status"),
    [
        ([Permissions.PAYMENT_VERIFICATION_VIEW_DETAILS], status.HTTP_200_OK),
        ([], status.HTTP_403_FORBIDDEN),
    ],
)
def test_verification_details(
    verification_context: dict[str, Any],
    permissions: list,
    expected_status: int,
    create_user_role_with_permissions: Any,
) -> None:
    url = reverse(
        "api:payments:verification-records-detail",
        kwargs={
            "business_area_slug": verification_context["business_area"].slug,
            "program_slug": verification_context["program_active"].slug,
            "payment_verification_pk": str(verification_context["payment_plan"].pk),
            "pk": str(verification_context["payment_1"].pk),
        },
    )
    create_user_role_with_permissions(
        verification_context["user"],
        permissions,
        verification_context["business_area"],
        verification_context["program_active"],
    )
    response = verification_context["client"].get(url)

    assert response.status_code == expected_status
    if expected_status == status.HTTP_200_OK:
        resp_data = response.json()
        assert "id" in resp_data
        assert "verification" in resp_data
        assert "id" in resp_data["verification"]
        assert "status" in resp_data["verification"]
        assert "verification_channel" in resp_data["verification"]
        assert "received_amount" in resp_data["verification"]


@pytest.mark.parametrize(
    ("permissions", "expected_status"),
    [
        (
            [
                Permissions.PAYMENT_VERIFICATION_VERIFY,
                Permissions.PAYMENT_VERIFICATION_VIEW_LIST,
            ],
            status.HTTP_200_OK,
        ),
        ([], status.HTTP_403_FORBIDDEN),
    ],
)
def test_update_verification(
    verification_context: dict[str, Any],
    permissions: list,
    expected_status: int,
    create_user_role_with_permissions: Any,
) -> None:
    url = reverse(
        "api:payments:verification-records-detail",
        kwargs={
            "business_area_slug": verification_context["business_area"].slug,
            "program_slug": verification_context["program_active"].slug,
            "payment_verification_pk": str(verification_context["payment_plan"].id),
            "pk": str(verification_context["payment_1"].pk),
        },
    )
    create_user_role_with_permissions(
        verification_context["user"],
        permissions,
        verification_context["business_area"],
        verification_context["program_active"],
    )
    verification_context["pvp"].status = PaymentVerificationPlan.STATUS_ACTIVE
    verification_context["pvp"].verification_channel = PaymentVerificationPlan.VERIFICATION_CHANNEL_MANUAL
    verification_context["pvp"].save()

    response = verification_context["client"].patch(
        url,
        {
            "version": verification_context["verification_1"].version,
            "received_amount": 123.22,
            "received": True,
        },
        format="multipart",
    )
    assert response.status_code == expected_status
    if expected_status == status.HTTP_200_OK:
        resp_data = response.json()

        assert "id" in resp_data
        assert resp_data["verification"]["received_amount"] == "123.22"


def test_verifications_list_filter_search(
    verification_context: dict[str, Any],
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        verification_context["user"],
        [Permissions.PAYMENT_VERIFICATION_VIEW_DETAILS],
        verification_context["business_area"],
        verification_context["program_active"],
    )
    url = reverse(
        "api:payments:verification-records-list",
        kwargs={
            "business_area_slug": verification_context["business_area"].slug,
            "program_slug": verification_context["program_active"].slug,
            "payment_verification_pk": str(verification_context["payment_plan"].pk),
        },
    )
    response = verification_context["client"].get(url, {"search": verification_context["payment_1"].unicef_id})
    assert response.status_code == status.HTTP_200_OK
    resp_data = response.json()["results"]
    assert len(resp_data) == 1
    assert resp_data[0]["unicef_id"] == verification_context["payment_1"].unicef_id


def test_verifications_list_filter_verification_status(
    verification_context: dict[str, Any],
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        verification_context["user"],
        [Permissions.PAYMENT_VERIFICATION_VIEW_DETAILS],
        verification_context["business_area"],
        verification_context["program_active"],
    )
    verification_context["verification_1"].status = PaymentVerification.STATUS_RECEIVED
    verification_context["verification_1"].save()
    verification_context["verification_2"].status = PaymentVerification.STATUS_PENDING
    verification_context["verification_2"].save()

    url = reverse(
        "api:payments:verification-records-list",
        kwargs={
            "business_area_slug": verification_context["business_area"].slug,
            "program_slug": verification_context["program_active"].slug,
            "payment_verification_pk": str(verification_context["payment_plan"].pk),
        },
    )
    response = verification_context["client"].get(url, {"verification_status": PaymentVerification.STATUS_RECEIVED})
    assert response.status_code == status.HTTP_200_OK
    resp_data = response.json()["results"]
    assert len(resp_data) == 1
    assert resp_data[0]["verification"]["status"] == PaymentVerification.STATUS_RECEIVED


def test_verifications_list_filter_verification_channel(
    verification_context: dict[str, Any],
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        verification_context["user"],
        [Permissions.PAYMENT_VERIFICATION_VIEW_DETAILS],
        verification_context["business_area"],
        verification_context["program_active"],
    )
    pvp_xlsx = PaymentVerificationPlanFactory(
        payment_plan=verification_context["payment_plan"],
        sampling=PaymentVerificationPlan.SAMPLING_FULL_LIST,
        verification_channel=PaymentVerificationPlan.VERIFICATION_CHANNEL_XLSX,
    )
    payment_3 = PaymentFactory(
        parent=verification_context["payment_plan"],
        status=Payment.STATUS_SUCCESS,
        delivered_quantity=200,
        entitlement_quantity=200,
    )
    PaymentVerificationFactory(
        payment_verification_plan=pvp_xlsx,
        payment=payment_3,
        status=PaymentVerification.STATUS_PENDING,
        status_date=timezone.now(),
    )

    url = reverse(
        "api:payments:verification-records-list",
        kwargs={
            "business_area_slug": verification_context["business_area"].slug,
            "program_slug": verification_context["program_active"].slug,
            "payment_verification_pk": str(verification_context["payment_plan"].pk),
        },
    )
    response = verification_context["client"].get(
        url,
        {"verification_channel": PaymentVerificationPlan.VERIFICATION_CHANNEL_MANUAL},
    )
    assert response.status_code == status.HTTP_200_OK
    resp_data = response.json()["results"]
    assert len(resp_data) == 2
    for payment in resp_data:
        assert payment["verification"]["verification_channel"] == PaymentVerificationPlan.VERIFICATION_CHANNEL_MANUAL


def test_verifications_list_filter_verification_plan_id(
    verification_context: dict[str, Any],
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        verification_context["user"],
        [Permissions.PAYMENT_VERIFICATION_VIEW_DETAILS],
        verification_context["business_area"],
        verification_context["program_active"],
    )
    pvp_2 = PaymentVerificationPlanFactory(
        payment_plan=verification_context["payment_plan"],
        sampling=PaymentVerificationPlan.SAMPLING_FULL_LIST,
        verification_channel=PaymentVerificationPlan.VERIFICATION_CHANNEL_XLSX,
    )
    payment_3 = PaymentFactory(
        parent=verification_context["payment_plan"],
        status=Payment.STATUS_SUCCESS,
        delivered_quantity=200,
        entitlement_quantity=200,
    )
    PaymentVerificationFactory(
        payment_verification_plan=pvp_2,
        payment=payment_3,
        status=PaymentVerification.STATUS_PENDING,
        status_date=timezone.now(),
    )

    url = reverse(
        "api:payments:verification-records-list",
        kwargs={
            "business_area_slug": verification_context["business_area"].slug,
            "program_slug": verification_context["program_active"].slug,
            "payment_verification_pk": str(verification_context["payment_plan"].pk),
        },
    )
    response = verification_context["client"].get(
        url,
        {"verification_plan_id": str(verification_context["pvp"].pk)},
    )
    assert response.status_code == status.HTTP_200_OK
    resp_data = response.json()["results"]
    assert len(resp_data) == 2
    for payment in resp_data:
        assert payment["verification"]["payment_verification_plan_unicef_id"] == verification_context["pvp"].unicef_id


def test_verifications_list_ordering(
    verification_context: dict[str, Any],
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        verification_context["user"],
        [Permissions.PAYMENT_VERIFICATION_VIEW_DETAILS],
        verification_context["business_area"],
        verification_context["program_active"],
    )
    url = reverse(
        "api:payments:verification-records-list",
        kwargs={
            "business_area_slug": verification_context["business_area"].slug,
            "program_slug": verification_context["program_active"].slug,
            "payment_verification_pk": str(verification_context["payment_plan"].pk),
        },
    )
    response_asc = verification_context["client"].get(url, {"ordering": "unicef_id"})
    assert response_asc.status_code == status.HTTP_200_OK
    resp_data_asc = response_asc.json()["results"]

    response_desc = verification_context["client"].get(url, {"ordering": "-unicef_id"})
    assert response_desc.status_code == status.HTTP_200_OK
    resp_data_desc = response_desc.json()["results"]

    assert resp_data_asc[0]["unicef_id"] == resp_data_desc[-1]["unicef_id"]
    assert resp_data_asc[-1]["unicef_id"] == resp_data_desc[0]["unicef_id"]
